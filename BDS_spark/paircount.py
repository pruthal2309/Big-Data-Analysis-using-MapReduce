import os
import sys

python_path = sys.executable

os.environ["PYSPARK_PYTHON"] = python_path
os.environ["PYSPARK_DRIVER_PYTHON"] = python_path

from pyspark.sql import SparkSession
from itertools import combinations
from collections import Counter
import re

# 1. Create Spark session
spark = (
    SparkSession.builder
    .appName("TweetWordCooccurrence")
    .master("local[*]")
    .config(
        "spark.hadoop.fs.defaultFS",
        "hdfs://localhost:9000"
    )
    .getOrCreate()
)

sc = spark.sparkContext
sc.setLogLevel("ERROR")

# 2. HDFS input and output paths
input_path = "hdfs://localhost:9000/tweets/tweet_data/*.txt"
output_path = "hdfs://localhost:9000/tweets/cooccurrence_output"

try:
    # 3. Read the data from HDFS
    lines = sc.textFile(input_path)

    # 4. Extract words from each line
    def extract_words(line):
        return re.findall(r"[a-zA-Z0-9']+", line.lower())

    # 5. Generate unique unordered pairs per line
    def generate_pairs(line):
        words = extract_words(line)

        # Count each pair at most once per line
        unique_words = sorted(set(words))

        return [
            (pair, 1)
            for pair in combinations(unique_words, 2)
        ]

    # 6. Generate pairs and count their co-occurrences
    pair_counts = (
        lines
        .flatMap(generate_pairs)
        .reduceByKey(lambda a, b: a + b)
    )

    # 7. Display top 20 co-occurring word pairs
    top_pairs = pair_counts.takeOrdered(
        20,
        key=lambda item: (-item[1], item[0])
    )

    print("\nTop 20 word co-occurrences:")
    for (word1, word2), count in top_pairs:
        print(f"{word1} - {word2}: {count}")

    # 8. Save all pair counts to HDFS
    pair_counts.map(
        lambda item: f"{item[0][0]}\t{item[0][1]}\t{item[1]}"
    ).saveAsTextFile(output_path)

    print("\nAll co-occurrence counts saved to:")
    print(output_path)

finally:
    spark.stop()
