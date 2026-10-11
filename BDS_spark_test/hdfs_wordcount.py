import os
import sys

python_path = sys.executable

os.environ["PYSPARK_PYTHON"] = python_path
os.environ["PYSPARK_DRIVER_PYTHON"] = python_path

from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("HadoopSparkWordCount")
    .master("local[*]")
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

input_path = "hdfs://localhost:9000/input2/input.txt"
output_path = "hdfs://localhost:9000/output_wordcount"

try:
    # Read the input file from Hadoop HDFS
    text = spark.sparkContext.textFile(input_path)

    # Count each word
    counts = (
        text.flatMap(lambda line: line.split())
            .map(lambda word: (word, 1))
            .reduceByKey(lambda a, b: a + b)
    )

    # Display results in the terminal
    print("WordCount results:")
    for word, count in sorted(counts.collect()):
        print(f"{word}: {count}")

    # Save results back to HDFS
    counts.saveAsTextFile(output_path)

    print(f"Results saved to {output_path}")

finally:
    spark.stop()
