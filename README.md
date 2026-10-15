# Big Data MapReduce + Spark ML Analysis Pipeline

A **hybrid big data architecture** demonstrating the synergy between Hadoop MapReduce (Phase 1) and Apache Spark ML (Phase 2).

## Architecture Overview

```
Common Crawl Data
      ↓
   DataCleaner (Java)
      ↓
   Hadoop HDFS
      ↓
   MapReduce ETL
   ├─ Word Count
   └─ Co-Occurrence Analysis
      ↓
   Output Files (text/tsv)
      ↓
   ┌──────────────┬──────────────┐
   │              │              │
   ↓              ↓              ↓
Dashboard    Spark ML      Analysis
(Streamlit)  (Phase 2)
```

## Phase 1: MapReduce ETL

**What it does:** One-pass distributed processing of Common Crawl text data
- **DataCleaner.java**: Preprocesses raw HTML/text into clean tokens
- **WordCount**: Counts word frequencies across entire corpus
- **CoOccurrence**: Identifies word pairs appearing in same context windows
- **TopN**: Extracts top-K frequent words

**Why MapReduce?** Fault-tolerant, disk-based processing ideal for large-scale ETL

## Phase 2: Spark ML (In-Memory Iterative ML)

**What it does:** Consumes MapReduce outputs for iterative machine learning
- **TF-IDF Vectorization**: Term importance scoring
- **K-Means Clustering**: Groups semantically related words
- **LDA Topic Modeling**: Discovers latent topics

**Why Spark?** In-memory processing enables iterative algorithms that would be too slow in MapReduce

## The Hybrid Advantage

| Concern | MapReduce | Spark |
|---------|-----------|-------|
| **Raw ETL** | ✅ Native strength | ❌ Overkill |
| **Fault Tolerance** | ✅ Built-in | ⚠️ Needs config |
| **Iterative ML** | ❌ Too slow | ✅ Optimized |
| **Memory Usage** | Low (disk-based) | High (in-memory) |

→ **Use MapReduce for ETL, Spark for ML**. No restructuring needed — the output files are the handoff point.

## Setup & Installation

### Prerequisites
- **Hadoop 3.3.6** (for MapReduce phase)
- **Java 8+** (for MapReduce jobs)
- **Python 3.9+** (for dashboard and Spark ML)

### Installation

1. **Clone the repository**
```bash
git clone <repo-url>
cd <repo-directory>
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Optional: PySpark for ML Phase**
```bash
# If the above didn't install PySpark, install separately:
pip install pyspark
```

## Running the Pipeline

### 1. Run MapReduce Jobs (already completed in your case)

The following MapReduce outputs should exist:
```
output/wordcount.txt          # Word frequencies
output/top10.txt              # Top 10 words
WordCooccurrenceOutput/coOccurrence/cooccurrence.txt  # Co-occurrence pairs
```

### 2. Launch the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

## Dashboard Features

### Tabs Overview

1. **📊 Word Frequency** — Bar charts, distributions, MapReduce top-10 verification
2. **☁️ Word Cloud** — Visual frequency representation
3. **🔥 Co-Occurrence Heatmap** — Pairwise word relationships
4. **🕸️ Word Network** — Graph visualization of word connections
5. **📋 Key Findings** — Statistical insights and patterns
6. **🔍 Word Explorer** — Interactive word relationship browser with clustering
7. **🚀 Spark ML** — In-memory ML pipelines (Phase 2)

### Spark ML Pipelines

**TF-IDF Vectorization**
- Computes term importance scores
- Identifies distinctive vocabulary
- Uses Spark HashingTF + IDF

**K-Means Clustering**
- Groups words by frequency patterns
- Feature engineering from co-occurrence stats
- Distributed clustering via MLlib

**LDA Topic Modeling**
- Discovers latent semantic topics
- Word-topic probability distributions
- Online LDA optimizer

## Data Flow

```
MapReduce Output Files
    ↓
Spark DataFrames (native text file readers)
    ↓
ML Feature Engineering
    ↓
Spark ML Pipelines
    ↓
Results → Dashboard Visualization
```

## Project Structure

```
.
├── src/                          # Java MapReduce source
│   ├── coOccurrence/            # Co-occurrence job
│   ├── preprocessing/           # DataCleaner
│   ├── TopN/                    # Top-N extraction
│   └── wordCount/               # Word count job
├── output/                       # MapReduce outputs
│   ├── wordcount.txt
│   └── top10.txt
├── WordCooccurrenceOutput/      # Co-occurrence results
├── dashboard.py                 # Streamlit dashboard (Phase 1 + 2)
├── spark_ml.py                  # Spark ML module (Phase 2)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Technical Details

### MapReduce Jobs
- **Language**: Java 8
- **Framework**: Hadoop 3.3.6
- **Input**: Common Crawl text data
- **Output Format**: Tab-separated values (TSV)

### Spark ML
- **Language**: Python (PySpark)
- **Version**: Spark 3.4+
- **Mode**: Local[*] (can scale to cluster)
- **Memory**: Configured for laptop use (1GB driver)

### Dashboard
- **Framework**: Streamlit
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Graph Analysis**: NetworkX
- **Word Clouds**: wordcloud library

## Why This Architecture?

1. **Separation of Concerns**: ETL (MapReduce) vs. ML (Spark)
2. **Cost Efficiency**: Disk-based for ETL, memory-based only when needed
3. **Fault Tolerance**: MapReduce handles large-scale failures better
4. **Iterative Performance**: Spark excels at ML algorithms
5. **No Duplication**: Single output format serves both phases

## Performance Notes

- MapReduce phase processes **millions of documents** from Common Crawl
- Spark ML operates on **filtered vocabulary** (top 200-500 words)
- Dashboard loads outputs in **<2 seconds**
- ML pipelines complete in **5-30 seconds** (local mode)

## Common Issues

**PySpark not installing?**
```bash
# Try with explicit version
pip install pyspark==3.4.0

# Or use conda
conda install -c conda-forge pyspark
```

**Dashboard won't start?**
```bash
# Check Streamlit installation
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit
```

**Spark ML tab shows error?**
- The dashboard works without PySpark
- Install PySpark to enable Phase 2 features

## Dataset

**Source**: Common Crawl
- Web-scale text corpus
- Real-world noise (HTML, JavaScript artifacts)
- Demonstrates production-grade data challenges

## License

[Your license here]

## Authors

[Your name/team]

## Acknowledgments

- Hadoop community for MapReduce framework
- Apache Spark for MLlib
- Streamlit for interactive dashboards
