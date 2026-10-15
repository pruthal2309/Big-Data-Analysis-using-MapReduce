"""
spark_ml.py  ──  Phase 2 : Spark In-Memory ML
===============================================
Reads the MapReduce output files produced in Phase 1
(output/wordcount.txt  +  WordCooccurrenceOutput/coOccurrence/cooccurrence.txt)
and streams them directly into PySpark DataFrames for iterative ML.

Three analysis pipelines are exposed:
  1. TF-IDF vectorisation  →  top-term importance scores
  2. K-Means clustering    →  word clusters from co-occurrence graph embeddings
  3. LDA topic modelling   →  latent topic extraction from word-frequency vectors

Each function returns a plain pandas DataFrame so Streamlit can render it
without needing to know anything about Spark internals.

Usage (from dashboard.py):
    from spark_ml import run_tfidf, run_kmeans, run_lda, get_spark_summary
"""

import os
import re
import math
from collections import defaultdict
from typing import Optional

import pandas as pd
import numpy as np

# ── PySpark imports ────────────────────────────────────────────────────────────
try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import (
        StructType, StructField, StringType, LongType, DoubleType, IntegerType
    )
    from pyspark.ml.feature import (
        HashingTF, IDF, Tokenizer, StopWordsRemover, VectorAssembler, Normalizer
    )
    from pyspark.ml.clustering import KMeans, LDA
    from pyspark.ml.linalg import Vectors, SparseVector
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False


# ── Paths (relative to project root) ──────────────────────────────────────────
WC_PATH   = "output/wordcount.txt"
COOC_PATH = "WordCooccurrenceOutput/coOccurrence/cooccurrence.txt"

# ── Noise filter (same as dashboard.py) ───────────────────────────────────────
_NOISE = {
    "a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z",
    "amp","nbsp","quot","apos","lt","gt",
    "http","https","www","com","org","net","html","htm","php",
    "charset","utf",
    "the","of","to","and","in","is","for","that","it","on",
    "are","was","with","as","at","be","by","this","an","or",
    "from","but","not","have","had","has","he","she","they",
    "we","you","his","her","their","our","its","been","were",
    "will","do","did","can","could","would","should","may",
    "might","shall","which","who","what","when","where","how",
    "if","then","than","so","all","more","also","about","up",
    "out","no","other","into","there","these","those","some",
    "over","after","before","while","any","each","one","two",
    "new","time","very","just","only","your","my","me","him",
    "them","us","via","per",
}


# ══════════════════════════════════════════════════════════════════════════════
# Internal helpers
# ══════════════════════════════════════════════════════════════════════════════

def _get_spark(app_name: str = "MapReduce-Spark-Phase2") -> "SparkSession":
    """Return (or create) a local SparkSession. Silences verbose Spark logs."""
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        # keep executor memory reasonable on a laptop
        .config("spark.driver.memory", "1g")
        .config("spark.sql.shuffle.partitions", "4")
        # suppress noisy INFO logs
        .config("spark.driver.extraJavaOptions", "-Dlog4j.rootCategory=WARN")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def _load_wordcount_pandas(top_n: int = 500) -> pd.DataFrame:
    """Load word-count file → clean pandas DataFrame (no Spark needed)."""
    rows = []
    try:
        with open(WC_PATH, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) != 2:
                    continue
                word, freq_str = parts[0].strip(), parts[1].strip()
                try:
                    freq = int(freq_str)
                except ValueError:
                    continue
                if re.match(r'^[a-z]{3,}$', word) and word not in _NOISE and freq >= 10:
                    rows.append((word, freq))
    except FileNotFoundError:
        pass
    df = pd.DataFrame(rows, columns=["word", "frequency"])
    df = df.sort_values("frequency", ascending=False).head(top_n).reset_index(drop=True)
    return df


def _load_cooccurrence_pandas(top_n: int = 5000) -> pd.DataFrame:
    """Load co-occurrence file → clean pandas DataFrame."""
    pairs = defaultdict(int)
    try:
        with open(COOC_PATH, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().rsplit("\t", 1)
                if len(parts) != 2:
                    continue
                pair_str, cnt_str = parts
                try:
                    count = int(cnt_str.strip())
                except ValueError:
                    continue
                ws = pair_str.strip().split()
                if len(ws) != 2:
                    continue
                w1, w2 = ws[0].strip(), ws[1].strip()
                if (re.match(r'^[a-z]{3,}$', w1) and
                        re.match(r'^[a-z]{3,}$', w2) and
                        w1 not in _NOISE and w2 not in _NOISE and
                        w1 != w2 and count >= 5):
                    key = tuple(sorted([w1, w2]))
                    pairs[key] += count
    except FileNotFoundError:
        pass
    rows = [{"word1": k[0], "word2": k[1], "count": v} for k, v in pairs.items()]
    df = pd.DataFrame(rows).sort_values("count", ascending=False).head(top_n).reset_index(drop=True)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def is_available() -> bool:
    """Return True if PySpark is installed and importable."""
    return PYSPARK_AVAILABLE


def get_spark_summary() -> dict:
    """Return a metadata dict about the Spark session (version, master, etc.)."""
    if not PYSPARK_AVAILABLE:
        return {"status": "PySpark not installed"}
    spark = _get_spark()
    return {
        "status"         : "Running",
        "spark_version"  : spark.version,
        "master"         : spark.sparkContext.master,
        "app_name"       : spark.sparkContext.appName,
        "default_parallelism": spark.sparkContext.defaultParallelism,
        "wc_records"     : _load_wordcount_pandas(top_n=999999).shape[0],
        "cooc_records"   : _load_cooccurrence_pandas(top_n=999999).shape[0],
    }


# ── Pipeline 1 : TF-IDF ───────────────────────────────────────────────────────

def run_tfidf(top_n: int = 200, num_features: int = 512) -> pd.DataFrame:
    """
    TF-IDF importance over the MapReduce word-frequency vocabulary.

    Strategy:
      - Treat each word as a "document" whose "text" is the word repeated
        proportional to its log-frequency (so rare words don't vanish).
      - Run Spark HashingTF → IDF to score each token.
      - Return a ranked DataFrame: word | raw_freq | tf_idf_score | rank

    Returns
    -------
    pd.DataFrame with columns: word, frequency, tfidf_score, rank
    """
    if not PYSPARK_AVAILABLE:
        return pd.DataFrame({"error": ["PySpark not installed"]})

    wc_pd = _load_wordcount_pandas(top_n=top_n)
    if wc_pd.empty:
        return pd.DataFrame({"error": ["Word count data not found"]})

    spark = _get_spark()

    # Build a synthetic "sentence" per word: word repeated log(freq) times
    # This lets IDF see realistic term-frequency variation
    def make_sentence(word: str, freq: int) -> str:
        repeat = max(1, int(math.log2(freq + 1)))
        return " ".join([word] * repeat)

    wc_pd["sentence"] = wc_pd.apply(
        lambda r: make_sentence(r["word"], r["frequency"]), axis=1
    )

    schema = StructType([
        StructField("word",      StringType(), False),
        StructField("frequency", LongType(),   False),
        StructField("sentence",  StringType(), False),
    ])

    # ── Load into Spark DataFrame ─────────────────────────────────────────────
    sdf = spark.createDataFrame(wc_pd[["word", "frequency", "sentence"]], schema=schema)

    # ── TF ────────────────────────────────────────────────────────────────────
    tokenizer = Tokenizer(inputCol="sentence", outputCol="tokens")
    tf_sdf    = tokenizer.transform(sdf)

    hashing_tf = HashingTF(numFeatures=num_features, inputCol="tokens", outputCol="raw_tf")
    tf_sdf     = hashing_tf.transform(tf_sdf)

    # ── IDF ───────────────────────────────────────────────────────────────────
    idf_model = IDF(inputCol="raw_tf", outputCol="tfidf").fit(tf_sdf)
    tfidf_sdf = idf_model.transform(tf_sdf)

    # ── Extract scalar TF-IDF score per word ─────────────────────────────────
    def vec_norm(v) -> float:
        if v is None:
            return 0.0
        arr = v.toArray()
        return float(np.linalg.norm(arr))

    vec_norm_udf = F.udf(vec_norm, DoubleType())
    result_sdf   = tfidf_sdf.withColumn("tfidf_score", vec_norm_udf(F.col("tfidf")))

    result_pd = (
        result_sdf
        .select("word", "frequency", "tfidf_score")
        .orderBy(F.col("tfidf_score").desc())
        .toPandas()
    )
    result_pd["rank"] = range(1, len(result_pd) + 1)
    result_pd["tfidf_score"] = result_pd["tfidf_score"].round(4)
    return result_pd


# ── Pipeline 2 : K-Means word clustering ─────────────────────────────────────

def run_kmeans(k: int = 6, top_n: int = 300) -> pd.DataFrame:
    """
    K-Means clustering of words using co-occurrence-based feature vectors.

    Strategy:
      - For each word in the top-N vocabulary, build a feature vector
        whose dimensions are: [raw_freq, degree (# unique co-occurrence partners),
        max_cooc_count, mean_cooc_count, log_freq].
      - Normalise with Spark Normalizer.
      - Fit KMeans(k) in Spark.
      - Return DataFrame: word | frequency | cluster | degree | max_cooc | mean_cooc

    Returns
    -------
    pd.DataFrame with columns: word, frequency, cluster, degree, max_cooc, mean_cooc
    """
    if not PYSPARK_AVAILABLE:
        return pd.DataFrame({"error": ["PySpark not installed"]})

    wc_pd   = _load_wordcount_pandas(top_n=top_n)
    cooc_pd = _load_cooccurrence_pandas(top_n=10000)

    if wc_pd.empty:
        return pd.DataFrame({"error": ["Word count data not found"]})

    # Build per-word co-occurrence stats
    vocab_set = set(wc_pd["word"])
    cooc_stats: dict[str, list] = defaultdict(list)
    for _, row in cooc_pd.iterrows():
        w1, w2, cnt = row["word1"], row["word2"], row["count"]
        if w1 in vocab_set:
            cooc_stats[w1].append(cnt)
        if w2 in vocab_set:
            cooc_stats[w2].append(cnt)

    rows = []
    for _, row in wc_pd.iterrows():
        w, freq = row["word"], int(row["frequency"])
        stats   = cooc_stats.get(w, [])
        degree  = len(stats)
        max_c   = max(stats) if stats else 0
        mean_c  = float(np.mean(stats)) if stats else 0.0
        log_f   = math.log1p(freq)
        rows.append({
            "word"     : w,
            "frequency": freq,
            "degree"   : degree,
            "max_cooc" : max_c,
            "mean_cooc": round(mean_c, 2),
            "log_freq" : log_f,
        })

    feat_pd = pd.DataFrame(rows)
    if feat_pd.empty:
        return pd.DataFrame({"error": ["No data after feature engineering"]})

    spark = _get_spark()

    schema = StructType([
        StructField("word",      StringType(), False),
        StructField("frequency", LongType(),   False),
        StructField("degree",    IntegerType(),False),
        StructField("max_cooc",  LongType(),   False),
        StructField("mean_cooc", DoubleType(), False),
        StructField("log_freq",  DoubleType(), False),
    ])

    sdf = spark.createDataFrame(feat_pd, schema=schema)

    # Assemble feature vector
    assembler = VectorAssembler(
        inputCols=["log_freq", "degree", "max_cooc", "mean_cooc"],
        outputCol="raw_features"
    )
    sdf = assembler.transform(sdf)

    # Normalise
    normalizer = Normalizer(inputCol="raw_features", outputCol="features", p=2.0)
    sdf        = normalizer.transform(sdf)

    # K-Means
    kmeans  = KMeans(k=k, seed=42, maxIter=50, featuresCol="features", predictionCol="cluster")
    model   = kmeans.fit(sdf)
    sdf_out = model.transform(sdf)

    result_pd = sdf_out.select(
        "word", "frequency", "cluster", "degree", "max_cooc", "mean_cooc"
    ).toPandas()

    result_pd = result_pd.sort_values(["cluster", "frequency"], ascending=[True, False])
    result_pd = result_pd.reset_index(drop=True)
    return result_pd


# ── Pipeline 3 : LDA topic modelling ─────────────────────────────────────────

def run_lda(num_topics: int = 5, top_n_words: int = 300, top_words_per_topic: int = 10) -> dict:
    """
    LDA (Latent Dirichlet Allocation) topic modelling over the word-frequency
    vocabulary using co-occurrence counts as the "document" signal.

    Strategy:
      - Treat each high-frequency word as a mini-document.
        Its "corpus" is the weighted bag of words formed by its top co-occurring
        neighbours (neighbour_word → co-occurrence count as TF).
      - Feed this into Spark HashingTF → IDF → LDA.
      - Extract top words per topic.

    Returns
    -------
    dict  {
        "topics"      : pd.DataFrame  (topic_id, top_words, weights),
        "word_topics" : pd.DataFrame  (word, dominant_topic, topic_distribution)
    }
    """
    if not PYSPARK_AVAILABLE:
        return {
            "topics"     : pd.DataFrame({"error": ["PySpark not installed"]}),
            "word_topics": pd.DataFrame(),
        }

    wc_pd   = _load_wordcount_pandas(top_n=top_n_words)
    cooc_pd = _load_cooccurrence_pandas(top_n=20000)

    if wc_pd.empty:
        return {
            "topics"     : pd.DataFrame({"error": ["Word count data not found"]}),
            "word_topics": pd.DataFrame(),
        }

    vocab_set = set(wc_pd["word"])

    # Build neighbour map  word → [(neighbour, count), ...]
    nbr_map: dict[str, list] = defaultdict(list)
    for _, row in cooc_pd.iterrows():
        w1, w2, cnt = row["word1"], row["word2"], int(row["count"])
        if w1 in vocab_set and w2 in vocab_set:
            nbr_map[w1].append((w2, cnt))
            nbr_map[w2].append((w1, cnt))

    # Sort neighbours by count descending
    for w in nbr_map:
        nbr_map[w].sort(key=lambda x: x[1], reverse=True)

    # Build "document" for each word: list of neighbour tokens, repeated proportionally
    doc_rows = []
    for _, row in wc_pd.iterrows():
        w, freq = row["word"], int(row["frequency"])
        nbrs = nbr_map.get(w, [])[:20]  # top-20 neighbours
        tokens = [w]  # self-token
        for nbr, cnt in nbrs:
            repeat = max(1, int(math.log2(cnt + 1)))
            tokens.extend([nbr] * repeat)
        doc_rows.append({"doc_id": w, "sentence": " ".join(tokens)})

    if not doc_rows:
        return {
            "topics"     : pd.DataFrame({"error": ["No co-occurrence neighbours found"]}),
            "word_topics": pd.DataFrame(),
        }

    doc_pd = pd.DataFrame(doc_rows)
    spark  = _get_spark()

    schema = StructType([
        StructField("doc_id",   StringType(), False),
        StructField("sentence", StringType(), False),
    ])
    sdf = spark.createDataFrame(doc_pd, schema=schema)

    # Tokenize
    tokenizer = Tokenizer(inputCol="sentence", outputCol="tokens")
    sdf = tokenizer.transform(sdf)

    # TF
    num_features = 256
    hashing_tf   = HashingTF(numFeatures=num_features, inputCol="tokens", outputCol="raw_tf")
    sdf = hashing_tf.transform(sdf)

    # IDF
    idf_model = IDF(inputCol="raw_tf", outputCol="features", minDocFreq=1).fit(sdf)
    sdf       = idf_model.transform(sdf)

    # LDA
    lda = LDA(
        k=num_topics, maxIter=20, seed=42,
        featuresCol="features", topicDistributionCol="topic_dist",
        optimizer="online",
    )
    lda_model = lda.fit(sdf)

    # ── Word-topic assignments ────────────────────────────────────────────────
    sdf_out    = lda_model.transform(sdf)
    result_sdf = sdf_out.select("doc_id", "topic_dist")

    def dominant_topic(v) -> int:
        if v is None:
            return 0
        arr = v.toArray()
        return int(np.argmax(arr))

    def topic_dist_str(v) -> str:
        if v is None:
            return ""
        arr = v.toArray()
        return " | ".join(f"T{i}:{arr[i]:.2f}" for i in range(len(arr)))

    dom_udf  = F.udf(dominant_topic, IntegerType())
    dist_udf = F.udf(topic_dist_str, StringType())

    result_sdf = (
        result_sdf
        .withColumn("dominant_topic",      dom_udf(F.col("topic_dist")))
        .withColumn("topic_distribution", dist_udf(F.col("topic_dist")))
    )

    word_topics_pd = result_sdf.select(
        F.col("doc_id").alias("word"),
        "dominant_topic",
        "topic_distribution",
    ).toPandas()

    # ── Extract top-N words per topic from LDA topic matrix ──────────────────
    topics_matrix = lda_model.describeTopics(maxTermsPerTopic=top_words_per_topic)
    topics_pd     = topics_matrix.toPandas()

    # Map feature indices back to approximate words using hashing_tf vocabulary
    # (HashingTF hashes to bucket — we label each bucket by the most-likely word)
    # Build a simple word → bucket mapping
    bucket_to_word: dict[int, str] = {}
    all_words = list(vocab_set)
    for w in all_words:
        h = hashing_tf.indexOf(w) if hasattr(hashing_tf, "indexOf") else abs(hash(w)) % num_features
        if h not in bucket_to_word:
            bucket_to_word[h] = w

    def indices_to_words(indices, weights) -> tuple[str, str]:
        words_found = []
        wts = []
        for idx, wt in zip(indices, weights):
            word_label = bucket_to_word.get(int(idx), f"feat_{idx}")
            words_found.append(word_label)
            wts.append(round(float(wt), 4))
        return ", ".join(words_found), " | ".join(map(str, wts))

    topic_rows = []
    for _, row in topics_pd.iterrows():
        topic_id = int(row["topic"])
        words_str, weights_str = indices_to_words(row["termIndices"], row["termWeights"])
        topic_rows.append({
            "topic_id"  : topic_id,
            "top_words" : words_str,
            "weights"   : weights_str,
        })

    topics_result_pd = pd.DataFrame(topic_rows)

    return {
        "topics"     : topics_result_pd,
        "word_topics": word_topics_pd,
    }
