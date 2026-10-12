import os
import sys

python_path = sys.executable

os.environ["PYSPARK_PYTHON"] = python_path
os.environ["PYSPARK_DRIVER_PYTHON"] = python_path

from pyspark.sql import SparkSession
import re

# 1. Create Spark session and connect to Hadoop HDFS
spark = (
    SparkSession.builder
    .appName("TweetWordCount")
    .master("local[*]")
    .config(
        "spark.hadoop.fs.defaultFS",
        "hdfs://localhost:9000"
    )
    .getOrCreate()
)

sc = spark.sparkContext
sc.setLogLevel("ERROR")

# 2. Input and output locations in HDFS
input_path = "hdfs://localhost:9000/tweets/tweet_data/*.txt"
output_path = "hdfs://localhost:9000/tweets/output_wordcount"

try:
    # 3. Read all text files from HDFS
    lines = sc.textFile(input_path)

    print("Input partitions:", lines.getNumPartitions())

    # 4. Convert text to lowercase words
    words = lines.flatMap(
        lambda line: re.findall(
            r"[a-zA-Z0-9']+", line.lower()
        )
    )

    # 5. Give each word an initial count of 1
    pairs = words.map(lambda word: (word, 1))

    # 6. Add counts for identical words
    counts = pairs.reduceByKey(lambda a, b: a + b)

    print("Output partitions:", counts.getNumPartitions())

    # 7. Display only the 20 most frequent words
    top_words = counts.takeOrdered(
        20, key=lambda item: (-item[1], item[0])
    )

    print("\nTop 20 most frequent words:")
    for word, count in top_words:
        print(f"{word}: {count}")

    # 8. Save ALL word counts to HDFS
    counts.saveAsTextFile(output_path)

    print("\nAll word counts saved to:", output_path)

finally:
    spark.stop()
