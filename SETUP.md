# Quick Setup Guide

## Phase 2: Spark ML Integration

This guide helps you set up the Spark ML capabilities to complement your existing MapReduce pipeline.

## Prerequisites Check

✅ **Already have:**
- Hadoop MapReduce outputs in `output/` and `WordCooccurrenceOutput/`
- Python 3.9+ installed
- Dashboard working (`dashboard.py`)

⚠️ **Need to add:**
- PySpark for ML capabilities

## Installation Steps

### Option 1: Quick Install (Recommended)

```bash
# Install all dependencies including PySpark
pip install -r requirements.txt
```

### Option 2: Manual Install

```bash
# Core dashboard dependencies
pip install streamlit pandas numpy matplotlib seaborn plotly wordcloud networkx

# Spark ML (Phase 2)
pip install pyspark
```

### Option 3: Conda Users

```bash
# Create new environment
conda create -n bigdata python=3.10
conda activate bigdata

# Install dependencies
conda install -c conda-forge streamlit pandas numpy matplotlib seaborn plotly
pip install wordcloud networkx pyspark
```

## Verification

### 1. Test PySpark Installation

```bash
python -c "from pyspark.sql import SparkSession; print('✅ PySpark installed')"
```

Expected output: `✅ PySpark installed`

### 2. Test Spark ML Module

```bash
python -c "import spark_ml; print(spark_ml.is_available())"
```

Expected output: `True`

### 3. Launch Dashboard

```bash
streamlit run dashboard.py
```

Navigate to the **🚀 Spark ML** tab to verify Phase 2 is working.

## What You'll See

### Without PySpark
- Dashboard works normally
- Tabs 1-6 function perfectly
- Tab 7 (Spark ML) shows installation instructions

### With PySpark
- All tabs functional
- Spark ML tab offers 3 pipelines:
  1. **TF-IDF Term Importance**
  2. **K-Means Word Clustering**
  3. **LDA Topic Modeling**

## Architecture Flow

```
Your Existing MapReduce Outputs
         ↓
    [Already working: output/wordcount.txt + cooccurrence.txt]
         ↓
    spark_ml.py reads these files
         ↓
    Converts to Spark DataFrames
         ↓
    Runs ML algorithms (TF-IDF, K-Means, LDA)
         ↓
    Returns pandas DataFrames
         ↓
    Dashboard visualizes results
```

## Performance Expectations

**Local Mode (your laptop):**
- TF-IDF: ~5-10 seconds
- K-Means: ~10-20 seconds  
- LDA: ~15-30 seconds

**Memory Usage:**
- Dashboard: ~200MB
- Spark session: ~1GB (configured conservatively)
- Total: ~1.2GB RAM needed

## Troubleshooting

### PySpark Won't Install

**Problem:** Pip fails with Java-related errors

**Solution:**
```bash
# Install specific version
pip install pyspark==3.4.0

# Or use conda
conda install -c conda-forge pyspark
```

### Java Not Found Error

**Problem:** Spark needs Java but can't find it

**Solution:**
```bash
# Install Java (if not already)
# Windows: Download from Oracle or use chocolatey
choco install openjdk11

# Verify
java -version
```

### Slow Spark Startup

**Problem:** First run takes 30+ seconds

**Solution:** This is normal — Spark initializes JVM. Subsequent runs are faster.

### Memory Errors

**Problem:** Spark crashes with OOM

**Solution:** Already configured for 1GB. If issues persist:
```python
# Edit spark_ml.py line ~97
.config("spark.driver.memory", "512m")  # Reduce from 1g
```

## Testing the Integration

### Quick Test Script

Create `test_spark.py`:
```python
import spark_ml

# Test availability
print(f"PySpark available: {spark_ml.is_available()}")

# Test summary
if spark_ml.is_available():
    summary = spark_ml.get_spark_summary()
    print(f"\nSpark version: {summary.get('spark_version')}")
    print(f"Word count records: {summary.get('wc_records')}")
    print(f"Co-occurrence records: {summary.get('cooc_records')}")
    
    # Quick TF-IDF test
    print("\nRunning TF-IDF test...")
    result = spark_ml.run_tfidf(top_n=20, num_features=128)
    print(f"✅ TF-IDF completed: {len(result)} results")
    print(result.head())
```

Run: `python test_spark.py`

## Next Steps

1. ✅ Install dependencies
2. ✅ Verify PySpark works
3. ✅ Launch dashboard
4. 🎯 Explore Spark ML tab
5. 🚀 Run each ML pipeline
6. 📊 Compare Phase 1 (MapReduce) vs Phase 2 (Spark ML) insights

## Key Differences: MapReduce vs Spark ML

| Feature | MapReduce (Phase 1) | Spark ML (Phase 2) |
|---------|--------------------|--------------------|
| **Best for** | One-pass ETL | Iterative algorithms |
| **Speed** | Moderate (disk I/O) | Fast (in-memory) |
| **Use case** | Counting, filtering | ML, clustering, modeling |
| **Output** | Text files | DataFrames → visualizations |
| **When to use** | Initial data processing | Advanced analysis on processed data |

## Support

If you encounter issues:
1. Check this guide's Troubleshooting section
2. Verify all prerequisites are installed
3. Check `requirements.txt` matches your Python version
4. The dashboard works even without PySpark (Tabs 1-6)

---

**Remember:** The Spark ML phase is *optional* but demonstrates how to extend MapReduce outputs with iterative machine learning. Your MapReduce pipeline is already complete and functional!
