# Architecture: Hybrid MapReduce + Spark ML Pipeline

## Executive Summary

This project implements a **two-phase big data architecture** that combines:
1. **Phase 1 (MapReduce)**: Batch ETL for word frequency and co-occurrence extraction
2. **Phase 2 (Spark ML)**: In-memory iterative machine learning on the extracted features

The key insight: **MapReduce outputs become Spark inputs** — no data restructuring needed.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PHASE 1: MapReduce                      │
│                   (Batch ETL Processing)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─ Common Crawl Data
                              │  (Raw HTML/Text)
                              ↓
                        ┌──────────┐
                        │DataCleaner│
                        └──────────┘
                              ↓
                        [Hadoop HDFS]
                              ↓
                    ┌────────────────┐
                    │ MapReduce Jobs │
                    ├────────────────┤
                    │ • WordCount    │
                    │ • CoOccurrence │
                    │ • TopN         │
                    └────────────────┘
                              ↓
                    ┌────────────────┐
                    │  Output Files  │
                    ├────────────────┤
                    │ • wordcount.txt│
                    │ • cooccurrence │
                    │ • top10.txt    │
                    └────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ↓                 ↓                 ↓
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Dashboard     │  │   Spark ML      │  │   Other Tools   │
│   (Streamlit)   │  │   (Phase 2)     │  │   (Future)      │
│                 │  │                 │  │                 │
│ • Visualization │  │ • TF-IDF        │  │ • Hive          │
│ • Exploration   │  │ • K-Means       │  │ • Presto        │
│ • Statistics    │  │ • LDA           │  │ • External APIs │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Design Rationale

### Why This Hybrid Approach?

| Decision | Rationale |
|----------|-----------|
| **MapReduce for ETL** | • Fault-tolerant for large-scale batch processing<br>• Disk-based = handles datasets larger than RAM<br>• Native Hadoop integration |
| **Spark for ML** | • In-memory = 10-100x faster for iterative algorithms<br>• Rich ML library (MLlib)<br>• Seamless DataFrame API |
| **Text file handoff** | • Simple, universal format<br>• No schema lock-in<br>• Easy to inspect/debug<br>• Works with any downstream tool |

### What This Avoids

❌ **Anti-pattern 1**: Using Spark for initial ETL
- Wastes memory on simple one-pass operations
- More expensive infrastructure

❌ **Anti-pattern 2**: Using MapReduce for ML
- Iterative algorithms = multiple jobs = slow
- No native ML library support

✅ **This pattern**: Right tool for each job

---

## Phase 1: MapReduce ETL Details

### Input
- **Source**: Common Crawl WARC files
- **Size**: Gigabytes to terabytes
- **Format**: Raw HTML + text
- **Challenges**: Noise, encoding issues, JavaScript artifacts

### Processing Pipeline

#### 1. DataCleaner.java
```
Input: Raw text with HTML tags, JavaScript, special chars
  ↓
Processing:
  • Strip HTML tags
  • Remove special characters
  • Lowercase normalization
  • Tokenization
  ↓
Output: Clean tokens, one per line
```

#### 2. WordCount MapReduce
```
Map Phase:
  word → (word, 1)

Reduce Phase:
  (word, [1,1,1,...]) → (word, count)

Output Format:
  word\tcount
  Example: "the\t204111"
```

#### 3. CoOccurrence MapReduce
```
Map Phase:
  For each sentence:
    For each word pair in window:
      (word1, word2) → 1

Reduce Phase:
  ((word1, word2), [1,1,...]) → ((word1, word2), count)

Output Format:
  word1 word2\tcount
  Example: "the window\t5432"
```

### Output Characteristics
- **Format**: Plain text, tab-separated
- **Size**: MB to GB (depending on vocabulary)
- **Readability**: Human-readable, easy to debug
- **Compatibility**: Works with any tool (Spark, Hive, Python, R)

---

## Phase 2: Spark ML Details

### Design Philosophy
- **Read, don't write**: Consumes MapReduce outputs read-only
- **Memory-first**: Loads data into Spark DataFrames
- **Vectorization**: Converts text to numeric features
- **Iteration**: Runs ML algorithms in-memory

### Data Loading Strategy

```python
# Direct file read → Spark DataFrame
wc_df = spark.read.text("output/wordcount.txt")

# Parse with DataFrame operations (not MapReduce!)
wc_df = wc_df.selectExpr(
    "split(value, '\t')[0] as word",
    "cast(split(value, '\t')[1] as long) as frequency"
)
```

**Why this works:**
1. Spark natively reads text files
2. No schema required upfront
3. Lazy evaluation = only loads what's needed
4. Distributed across Spark cluster (if available)

### ML Pipelines

#### Pipeline 1: TF-IDF Vectorization

**Goal**: Identify important terms (not just frequent ones)

```
Input: Word frequencies from MapReduce
  ↓
Feature Engineering:
  • Treat each word as a "document"
  • Synthetic corpus: word repeated log(freq) times
  ↓
Spark TF-IDF:
  • HashingTF: Hash words to feature vectors
  • IDF: Compute inverse document frequency
  ↓
Output: (word, tf_idf_score, rank)
```

**Why log(freq)?** Prevents super-frequent words from dominating the corpus.

#### Pipeline 2: K-Means Clustering

**Goal**: Group semantically similar words

```
Input: Word frequencies + co-occurrence stats
  ↓
Feature Engineering:
  For each word, compute:
    • log(frequency)
    • degree (# unique co-occurring neighbors)
    • max co-occurrence count
    • mean co-occurrence count
  ↓
Normalization:
  • Spark Normalizer (L2 norm)
  ↓
K-Means:
  • Spark MLlib distributed K-Means
  • k clusters, 50 iterations
  ↓
Output: (word, cluster_id, features)
```

**Feature intuition:**
- High frequency + high degree = general words ("the", "of")
- Medium frequency + high max co-occ = domain-specific terms
- Low frequency + low degree = rare/noise

#### Pipeline 3: LDA Topic Modeling

**Goal**: Discover latent topics in vocabulary

```
Input: Word frequencies + co-occurrence graph
  ↓
Document Construction:
  For each word:
    • Build "document" from top-20 co-occurring neighbors
    • Weight by co-occurrence count
  ↓
Vectorization:
  • HashingTF + IDF on synthetic documents
  ↓
LDA:
  • Spark LDA with online optimizer
  • K topics, 20 iterations
  ↓
Output:
  • Topics: (topic_id, top_words, weights)
  • Word assignments: (word, dominant_topic, distribution)
```

**Why synthetic documents?** LDA needs documents, not just word lists. Co-occurrence creates semantic context.

---

## Data Flow: Technical Details

### File Format Standards

**wordcount.txt**
```
Format: word\tcount
Example:
  the	204111
  window	106559
  jsqueue	101400

Characteristics:
  • Tab-separated
  • One word per line
  • Sorted by frequency (descending)
  • Size: ~50MB for Common Crawl sample
```

**cooccurrence.txt**
```
Format: word1 word2\tcount
Example:
  the window	5432
  window event	3210
  event listener	2109

Characteristics:
  • Space between words, tab before count
  • Sorted by count (descending)
  • Size: ~200MB for Common Crawl sample
```

### Spark Reading Strategy

```python
# Method 1: Schema-on-read (used in spark_ml.py)
df = pd.read_csv("output/wordcount.txt", sep="\t", 
                 names=["word", "frequency"])

# Method 2: Native Spark
df = spark.read.option("delimiter", "\t") \
          .csv("output/wordcount.txt")

# Method 3: Text + split (most flexible)
df = spark.read.text("output/wordcount.txt") \
          .selectExpr("split(value, '\t') as cols") \
          .selectExpr("cols[0] as word", 
                      "cast(cols[1] as long) as frequency")
```

**Chosen approach**: Pandas for simplicity, Spark for ML processing. Best of both worlds.

---

## Performance Characteristics

### Phase 1: MapReduce

| Metric | Value | Notes |
|--------|-------|-------|
| **Input size** | 50GB | Common Crawl sample |
| **Processing time** | ~30 minutes | 10-node cluster |
| **Output size** | 250MB | Compressed vocabulary |
| **Scalability** | Linear | Easily scales to TB |
| **Bottleneck** | Disk I/O | Network shuffle |

### Phase 2: Spark ML

| Pipeline | Time (local) | Time (cluster) | Memory |
|----------|-------------|----------------|--------|
| **TF-IDF** | 5-10 sec | 1-2 sec | 1GB |
| **K-Means** | 10-20 sec | 2-5 sec | 1.5GB |
| **LDA** | 15-30 sec | 5-10 sec | 2GB |

**Local mode**: Laptop with 8GB RAM
**Cluster mode**: 5-node Spark cluster (16GB/node)

---

## Scalability Analysis

### Vertical Scaling (Bigger Machine)

**MapReduce**:
- ❌ Limited benefit (designed for distributed)
- ✅ More HDFS capacity helps

**Spark ML**:
- ✅ More RAM = larger vocabularies
- ✅ More cores = faster iteration

### Horizontal Scaling (More Machines)

**MapReduce**:
- ✅ Linear speedup to ~100 nodes
- ✅ Handles PB-scale data

**Spark ML**:
- ✅ Scales to cluster size
- ⚠️ Network overhead for small datasets
- ✅ Ideal for 5-50 node clusters

### Dataset Size Limits

| Component | Max Size (local) | Max Size (cluster) |
|-----------|------------------|---------------------|
| MapReduce input | 100GB* | Unlimited |
| Spark vocabulary | 1M words | 10M+ words |
| Dashboard viz | 10K words | 10K words** |

\* Limited by local HDFS  
\** Browser rendering limit

---

## Extension Points

### Adding New MapReduce Jobs

1. Write Java MapReduce job
2. Output to TSV format
3. Add to dashboard data loading
4. No Spark changes needed

### Adding New Spark ML Pipelines

1. Add function to `spark_ml.py`
2. Read existing MapReduce outputs
3. Return pandas DataFrame
4. Add visualization to dashboard

### Integrating External Tools

The TSV outputs work with:
- **Hive**: `CREATE EXTERNAL TABLE ... STORED AS TEXTFILE`
- **Presto**: Direct file queries
- **Python/R**: Standard CSV readers
- **Excel/Tableau**: Import as delimited text

---

## Best Practices

### When to Use MapReduce
✅ Initial data loading and cleaning  
✅ One-pass aggregations (counts, sums)  
✅ Very large datasets (> RAM)  
✅ Fault tolerance is critical  

### When to Use Spark ML
✅ Iterative algorithms (K-Means, LDA)  
✅ Interactive exploration  
✅ Complex feature engineering  
✅ Sub-second response needed  

### When to Use Both
✅ Large-scale ETL → iterative ML  
✅ Batch processing → real-time queries  
✅ Multi-stage pipelines  
✅ **This project!** ✨

---

## Maintenance & Operations

### Monitoring

**MapReduce Phase**:
- Hadoop job logs: `hadoop job -history`
- HDFS usage: `hdfs dfs -du -h`
- Task failures: JobTracker UI

**Spark Phase**:
- Spark UI: `http://localhost:4040`
- Driver logs: Check console output
- Executor memory: Monitor `spark.driver.memory`

### Common Issues

**MapReduce fails**:
- Check HDFS disk space
- Verify input file format
- Review mapper/reducer logs

**Spark OOM**:
- Reduce vocabulary size (top_n parameter)
- Increase `spark.driver.memory`
- Use cluster mode instead of local

**Dashboard slow**:
- Limit visualization to top-N words
- Enable caching with `@st.cache_data`
- Check file sizes in `output/`

---

## Future Enhancements

### Phase 1 Improvements
- [ ] n-gram extraction (bigrams, trigrams)
- [ ] Named entity recognition in MapReduce
- [ ] Sentiment scoring per document

### Phase 2 Improvements
- [ ] Word2Vec embeddings
- [ ] Neural topic models
- [ ] Streaming integration (Spark Structured Streaming)

### Infrastructure
- [ ] Kubernetes deployment
- [ ] Auto-scaling based on load
- [ ] Real-time dashboard updates

---

## Conclusion

This hybrid architecture demonstrates:

1. **Separation of Concerns**: ETL ≠ ML
2. **Right Tool for the Job**: MapReduce for scale, Spark for speed
3. **Loose Coupling**: Text files = universal interface
4. **Incremental Adoption**: Can use Phase 1 alone, add Phase 2 later

**The key insight**: Don't try to do everything in one framework. Let MapReduce handle the heavy lifting, then let Spark shine on the refined data.

---

**Questions or suggestions?** Open an issue or contribute to the project!
