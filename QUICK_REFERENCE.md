# Quick Reference Card

## Phase 2: Spark ML Integration

### 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboard.py

# Navigate to Tab 7: Spark ML
```

---

## 📂 File Structure

```
├── dashboard.py              # Main dashboard (Tab 7 = Spark ML)
├── spark_ml.py              # Spark ML module (3 pipelines)
├── requirements.txt         # Python dependencies
├── output/
│   ├── wordcount.txt       # MapReduce output (480 KB)
│   └── top10.txt           # Top 10 words
└── WordCooccurrenceOutput/
    └── coOccurrence/
        └── cooccurrence.txt # Co-occurrence pairs (3.6 MB)
```

---

## 🎯 ML Pipelines Available

### 1. TF-IDF Term Importance

**What**: Identifies important terms (not just frequent ones)  
**Input**: wordcount.txt  
**Output**: (word, tf_idf_score, rank)  
**Use Case**: Find distinctive vocabulary

**Example**:
```python
result = spark_ml.run_tfidf(top_n=100, num_features=512)
# Returns: DataFrame with TF-IDF scores
```

### 2. K-Means Clustering

**What**: Groups semantically related words  
**Input**: wordcount.txt + cooccurrence.txt  
**Output**: (word, cluster_id, features)  
**Use Case**: Discover word categories

**Example**:
```python
result = spark_ml.run_kmeans(k=6, top_n=200)
# Returns: DataFrame with cluster assignments
```

### 3. LDA Topic Modeling

**What**: Discovers latent topics  
**Input**: wordcount.txt + cooccurrence.txt  
**Output**: (topics, word_assignments)  
**Use Case**: Understand corpus themes

**Example**:
```python
result = spark_ml.run_lda(num_topics=5, top_n_words=200)
# Returns: Dict with 'topics' and 'word_topics' DataFrames
```

---

## 🔧 Common Commands

### Installation

```bash
# Full install (with PySpark)
pip install -r requirements.txt

# Minimal install (dashboard only, no Spark ML)
pip install streamlit pandas numpy matplotlib seaborn plotly wordcloud networkx
```

### Testing

```bash
# Run test suite
python test_spark_integration.py

# Test PySpark availability
python -c "import spark_ml; print(spark_ml.is_available())"

# Test specific pipeline
python -c "import spark_ml; print(spark_ml.run_tfidf(top_n=20))"
```

### Dashboard

```bash
# Start dashboard
streamlit run dashboard.py

# Access at: http://localhost:8501

# Stop dashboard: Ctrl+C
```

---

## 📊 Dashboard Tabs

| Tab | Name | Description | Status |
|-----|------|-------------|--------|
| 1 | Word Frequency | Bar charts, distributions | ✅ Working |
| 2 | Word Cloud | Visual frequency representation | ✅ Working |
| 3 | Co-Occurrence Heatmap | Pairwise relationships | ✅ Working |
| 4 | Word Network | Graph visualization | ✅ Working |
| 5 | Key Findings | Statistical insights | ✅ Working |
| 6 | Word Explorer | Interactive browsing | ✅ Working |
| 7 | **Spark ML** | **ML pipelines** | **🚀 NEW** |

---

## 🎛️ Parameters Guide

### TF-IDF

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `top_n` | 100 | 20-200 | Number of words to process |
| `num_features` | 512 | 128-1024 | Feature vector dimensions |

### K-Means

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `k` | 6 | 3-12 | Number of clusters |
| `top_n` | 150 | 50-300 | Vocabulary size |

### LDA

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `num_topics` | 5 | 3-10 | Number of topics to discover |
| `top_n_words` | 200 | 100-300 | Vocabulary size |
| `top_words_per_topic` | 10 | 5-15 | Words shown per topic |

---

## 🔍 Troubleshooting

### Issue: PySpark not found

```bash
# Solution:
pip install pyspark

# Or specific version:
pip install pyspark==3.4.0
```

### Issue: Dashboard won't start

```bash
# Check Streamlit:
streamlit --version

# Reinstall:
pip install --upgrade streamlit
```

### Issue: Spark ML tab shows error

```bash
# Verify PySpark:
python -c "from pyspark.sql import SparkSession; print('OK')"

# Check test suite:
python test_spark_integration.py
```

### Issue: Java not found (Windows)

```bash
# Install Java:
choco install openjdk11

# Or download from: https://adoptium.net/
```

### Issue: Memory errors

```python
# Edit spark_ml.py line ~97:
.config("spark.driver.memory", "512m")  # Reduce from 1g
```

---

## 📈 Performance Expectations

### Local Mode (Laptop)

| Pipeline | Time | Memory | Output |
|----------|------|--------|--------|
| TF-IDF | 5-10s | 1 GB | ~100 scored words |
| K-Means | 10-20s | 1.5 GB | Clusters + assignments |
| LDA | 15-30s | 2 GB | Topics + distributions |

### Cluster Mode (5 nodes)

| Pipeline | Time | Memory | Output |
|----------|------|--------|--------|
| TF-IDF | 1-2s | 8 GB | ~1000 scored words |
| K-Means | 2-5s | 12 GB | Larger vocabulary |
| LDA | 5-10s | 16 GB | More topics |

---

## 🏗️ Architecture Quick View

```
MapReduce (Phase 1)    Spark ML (Phase 2)
──────────────────     ──────────────────
• Word Count      →    • TF-IDF
• Co-Occurrence   →    • K-Means
• TopN            →    • LDA

Output Files (TSV) ← Bridge Point → Spark DataFrames
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Overview, setup, architecture |
| `SETUP.md` | Detailed installation guide |
| `ARCHITECTURE.md` | Design decisions deep-dive |
| `IMPLEMENTATION_SUMMARY.md` | What was built |
| `PHASE2_DIAGRAM.txt` | Visual architecture |
| `QUICK_REFERENCE.md` | This file |

---

## 💡 Key Concepts

### Hybrid Architecture

- **Phase 1 (MapReduce)**: One-pass ETL, disk-based, scales to PB
- **Phase 2 (Spark ML)**: Iterative ML, in-memory, 10-100x faster
- **Bridge**: Text files (TSV format), universal interface

### Why This Works

1. **Separation**: ETL ≠ ML (different tools, different strengths)
2. **Loose Coupling**: Text files = any tool can read
3. **Incremental**: Phase 2 optional, Phase 1 works alone
4. **Production-Ready**: Both phases scale independently

---

## 🎯 Common Tasks

### View MapReduce Results

```bash
# Word frequencies
head -20 output/wordcount.txt

# Co-occurrences
head -20 WordCooccurrenceOutput/coOccurrence/cooccurrence.txt
```

### Test Spark Integration

```bash
# Full test suite
python test_spark_integration.py

# Quick check
python -c "import spark_ml; print(spark_ml.get_spark_summary())"
```

### Run ML Pipeline Manually

```python
import spark_ml

# TF-IDF
df = spark_ml.run_tfidf(top_n=50, num_features=256)
print(df.head(10))

# K-Means
df = spark_ml.run_kmeans(k=4, top_n=100)
print(df['cluster'].value_counts())

# LDA
result = spark_ml.run_lda(num_topics=3, top_n_words=100)
print(result['topics'])
```

---

## ✅ Checklist

### Before Starting

- [ ] Python 3.9+ installed
- [ ] MapReduce outputs exist (wordcount.txt, cooccurrence.txt)
- [ ] Have 2+ GB RAM available

### Installation

- [ ] `pip install -r requirements.txt` completed
- [ ] No errors during installation
- [ ] Test suite passes

### Verification

- [ ] Dashboard loads without errors
- [ ] Tab 7 visible
- [ ] Can select ML pipeline
- [ ] Visualizations render correctly

---

## 🆘 Getting Help

### Check These First

1. **Test suite**: `python test_spark_integration.py`
2. **Documentation**: Read `SETUP.md` for detailed steps
3. **Logs**: Check terminal output for error messages

### Common Solutions

- **Import errors**: Reinstall requirements
- **PySpark issues**: Try `conda install -c conda-forge pyspark`
- **Memory errors**: Reduce parameters (smaller top_n, fewer topics)
- **Dashboard frozen**: Restart with Ctrl+C, then `streamlit run dashboard.py`

---

## 📞 Support Resources

- **SETUP.md**: Installation troubleshooting
- **ARCHITECTURE.md**: Understanding design
- **test_spark_integration.py**: Automated diagnostics
- **Dashboard error messages**: In-app guidance

---

## 🎉 Success Indicators

Your setup is working if:

✅ Test suite shows "Data Files: PASS"  
✅ Dashboard loads in browser  
✅ Tab 7 is visible  
✅ Can click "Run TF-IDF" button  
✅ Results appear in < 30 seconds  

---

**Quick Reference Complete** • Version 1.0 • Phase 2 Implementation
