# Big Data MapReduce Project — Complete Machine & Project Context

## Purpose

This file is the persistent context/reference for the project. Anyone continuing the project should read it before giving commands so they know where the software, source code, datasets, HDFS data, outputs, and remaining tasks are located.

---

## 1. Project Identity

**Project:** Big Data Analysis using MapReduce in Hadoop

**Original reference repository:**  
https://github.com/Mgosi/Big-Data-Analysis-using-MapReduce-in-Hadoop

**Current implementation repository:**  
https://github.com/pruthal2309/Big-Data-Analysis-using-MapReduce.git

The original project performs:

1. Data collection from Twitter, New York Times, and Common Crawl
2. Data preprocessing
3. HDFS storage
4. MapReduce Word Count
5. Word Co-Occurrence
6. Python analysis
7. Word-cloud / Tableau visualization
8. Final trend analysis

Our implementation is being rebuilt from scratch rather than blindly copying the original project.

---

# 2. Machine / Operating System

- Windows
- Hadoop is installed and running directly on Windows
- Main Hadoop commands are run from CMD
- PowerShell is also used for Git/project commands
- WSL is used for other college practicals, but this Hadoop project is currently a Windows Hadoop installation

### Important

Current project:

`E:\Big-Data-Mapper-Reducer`

---

# 3. Java Setup

Java 8 is being used.

```text
JAVA_HOME=C:\Java\jdk-8.0.492.9-hotspot
```

Check:

```cmd
java -version
javac -version
echo %JAVA_HOME%
```

---

# 4. Hadoop Setup

Version:

```text
Hadoop 3.3.6
```

Installation:

```text
C:\hadoop-3.3.6
```

Environment variable:

```text
HADOOP_HOME=C:\hadoop-3.3.6
```

Check:

```cmd
echo %HADOOP_HOME%
```

Important Hadoop libraries:

```text
C:\hadoop-3.3.6\share\hadoop\common
C:\hadoop-3.3.6\share\hadoop\common\lib
C:\hadoop-3.3.6\share\hadoop\hdfs
C:\hadoop-3.3.6\share\hadoop\hdfs\lib
C:\hadoop-3.3.6\share\hadoop\mapreduce
C:\hadoop-3.3.6\share\hadoop\mapreduce\lib
C:\hadoop-3.3.6\share\hadoop\yarn
C:\hadoop-3.3.6\share\hadoop\yarn\lib
```

---

# 5. Hadoop Components

```text
HDFS
 ├── NameNode
 └── DataNode

YARN
 ├── ResourceManager
 └── NodeManager

MapReduce
 ├── Mapper
 └── Reducer
```

Start:

```cmd
start-dfs.cmd
start-yarn.cmd
```

Stop:

```cmd
stop-yarn.cmd
stop-dfs.cmd
```

Check YARN:

```cmd
yarn node -list
```

Check applications:

```cmd
yarn application -list
```

Check HDFS:

```cmd
hdfs dfs -ls /
```

---

# 6. Hadoop Web Interfaces

ResourceManager:

```text
http://localhost:8088
```

NameNode:

```text
http://localhost:9870
```

ResourceManager is useful for checking:

- Application ID
- Map progress
- Reduce progress
- Start/finish time
- State
- Final status
- Memory
- CPU/vcores

---

# 7. Main Project Directory

```text
E:\Big-Data-Mapper-Reducer
```

Recommended:

```cmd
E:
cd E:\Big-Data-Mapper-Reducer
```

If CMD currently shows:

```text
C:\Windows\System32>
```

relative paths such as `bin` or `src` refer to the wrong location. Always move into the project first.

---

# 8. Project Structure

```text
E:\Big-Data-Mapper-Reducer\
│
├── .vscode\
│   └── settings.json
│
├── data\
│   ├── raw\
│   │   └── CommonCrawlData\
│   │       ├── ArticleBooks1.txt
│   │       ├── ArticleBooks2.txt
│   │       └── ...
│   │
│   └── processed\
│       └── CommonCrawlData\
│           ├── CleanedArticleBooks1.txt
│           ├── CleanedArticleBooks2.txt
│           └── ...
│
├── src\
│   ├── processing\
│   │   └── DataCleaner.java
│   │
│   ├── wordCount\
│   │   ├── WordCount.java
│   │   ├── WordCountMapper.java
│   │   └── WordCountReducer.java
│   │
│   └── coOccurrence\
│       ├── CoOccurrence.java
│       ├── CoOccurrenceMapper.java
│       └── CoOccurrenceReducer.java
│
├── bin\
├── wc.jar
├── cooccurrence.jar
├── output\
│   └── wordcount.txt
├── README.md
└── 1_Steps.txt / steps.md
```

Additional folders/files may be added later for Top-N, Python analysis, visualization, etc.

---

# 9. VS Code Configuration

File:

```text
E:\Big-Data-Mapper-Reducer\.vscode\settings.json
```

Current configuration:

```json
{
    "java.project.sourcePaths": [
        "src"
    ],
    "java.project.outputPath": "bin",
    "java.project.referencedLibraries": [
        "C:/hadoop-3.3.6/share/hadoop/**/*.jar"
    ],
    "explorer.compactFolders": false
}
```

This makes VS Code display:

```text
src
├── processing
├── wordCount
└── coOccurrence
```

instead of collapsing folders.

---

# 10. Java Packages

Folder and package names must match.

### Processing

```text
src\processing
```

```java
package processing;
```

### Word Count

```text
src\wordCount
```

```java
package wordCount;
```

### Co-Occurrence

```text
src\coOccurrence
```

```java
package coOccurrence;
```

---

# 11. Overall Current Pipeline

```text
Raw Common Crawl
      |
      v
data/raw/CommonCrawlData
      |
      v
DataCleaner.java
      |
      v
data/processed/CommonCrawlData
      |
      v
HDFS /BigData/CommonCrawlData
      |
      +--------------------+
      |                    |
      v                    v
 Word Count          Co-Occurrence
      |                    |
      v                    v
 Top Words              Pairs
      |                    |
      +---------+----------+
                |
                v
        Python Analysis
                |
                v
      Word Cloud / Tableau
```

---

# 12. Raw Common Crawl Data

Raw files are stored here:

```text
E:\Big-Data-Mapper-Reducer\data\raw\CommonCrawlData
```

Example:

```text
ArticleBooks1.txt
ArticleBooks2.txt
ArticleBooks3.txt
...
```

**Do not modify raw files directly.**

---

# 13. Processed Common Crawl Data

Cleaned files:

```text
E:\Big-Data-Mapper-Reducer\data\processed\CommonCrawlData
```

Example:

```text
CleanedArticleBooks1.txt
CleanedArticleBooks2.txt
CleanedArticleBooks3.txt
...
```

---

# 14. DataCleaner.java

Location:

```text
src\processing\DataCleaner.java
```

Current cleaner:

- processes all `.txt` files in a folder
- converts to lowercase
- removes URLs
- removes HTML tags
- removes punctuation/special characters
- normalizes whitespace
- writes cleaned files with `Cleaned` prefix

Run:

```cmd
E:
cd E:\Big-Data-Mapper-Reducer

javac -d bin src\processing\DataCleaner.java

java -cp bin processing.DataCleaner data\raw\CommonCrawlData data\processed\CommonCrawlData
```

The cleaning step has already been completed successfully.

---

# 15. Difference From Original Cleaning

The original repository describes:

1. Tokenization
2. Lowercase
3. Remove punctuation/special characters
4. Remove numbers
5. Remove stop words
6. Stemming and lemmatization
7. Reconstruct text

Our current Java cleaner does:

- lowercase
- URL removal
- HTML removal
- punctuation/special-character removal
- whitespace normalization

It does **not** currently perform full stop-word removal, stemming, or lemmatization.

This is an optional future improvement.

---

# 16. HDFS Input

HDFS Common Crawl input:

```text
/BigData/CommonCrawlData
```

Create:

```cmd
hdfs dfs -mkdir -p /BigData/CommonCrawlData
```

Upload:

```cmd
hdfs dfs -put data\processed\CommonCrawlData\* /BigData/CommonCrawlData/
```

Check:

```cmd
hdfs dfs -ls /BigData/CommonCrawlData
```

This upload has already been done.

---

# 17. Word Count Source

```text
src\wordCount\WordCount.java
src\wordCount\WordCountMapper.java
src\wordCount\WordCountReducer.java
```

JAR:

```text
E:\Big-Data-Mapper-Reducer\wc.jar
```

---

# 18. Word Count Logic

Example input:

```text
Machine learning is powerful
```

Mapper emits:

```text
<machine, 1>
<learning, 1>
<is, 1>
<powerful, 1>
```

Hadoop performs:

```text
Shuffle + Sort
```

Reducer receives all values for the same word and sums them:

```text
<machine, frequency>
```

---

# 19. Word Count Compilation

From the project directory:

```cmd
javac -classpath "%HADOOP_HOME%\share\hadoop\common\*;%HADOOP_HOME%\share\hadoop\common\lib\*;%HADOOP_HOME%\share\hadoop\hdfs\*;%HADOOP_HOME%\share\hadoop\hdfs\lib\*;%HADOOP_HOME%\share\hadoop\mapreduce\*;%HADOOP_HOME%\share\hadoop\mapreduce\lib\*;%HADOOP_HOME%\share\hadoop\yarn\*;%HADOOP_HOME%\share\hadoop\yarn\lib\*" -d bin src\wordCount\*.java
```

Create JAR:

```cmd
jar -cvf wc.jar -C bin .
```

---

# 20. Word Count Execution

Input:

```text
/BigData/CommonCrawlData
```

Output:

```text
/BigData/CommonCrawlWordCount
```

Run:

```cmd
hadoop jar wc.jar wordCount.WordCount /BigData/CommonCrawlData /BigData/CommonCrawlWordCount
```

If output already exists:

```cmd
hdfs dfs -rm -r /BigData/CommonCrawlWordCount
```

then rerun.

---

# 21. Word Count Status — COMPLETED

The full Word Count MapReduce job successfully completed.

HDFS output contained:

```text
_SUCCESS
part-r-00000
```

Previously observed:

```text
/BigData/CommonCrawlWordCount/_SUCCESS
/BigData/CommonCrawlWordCount/part-r-00000
```

`_SUCCESS` confirms successful completion.

`part-r-00000` contains reducer output.

Observed reducer output size was approximately:

```text
480031 bytes
```

ResourceManager also showed:

```text
State: FINISHED
Final Status: SUCCEEDED
Application Type: MAPREDUCE
Name: Word Count
```

Therefore Word Count is DONE.

---

# 22. Local Word Count Output

Local directory:

```text
E:\Big-Data-Mapper-Reducer\output
```

Copy:

```cmd
mkdir output
hdfs dfs -get /BigData/CommonCrawlWordCount/part-r-00000 output\wordcount.txt
```

Local file:

```text
E:\Big-Data-Mapper-Reducer\output\wordcount.txt
```

This is the input for Top-10 analysis.

---

# 23. Top 10 Words

The original project uses the Top 10 words from Word Count for Co-Occurrence.

A `TopNWords.java` implementation has been planned/provided.

Expected location:

```text
src\topN\TopNWords.java
```

Input:

```text
output\wordcount.txt
```

Expected logic:

```text
wordcount.txt
     |
     v
read word + frequency
     |
     v
min-heap of size 10
     |
     v
Top 10 words
```

This still needs to be finalized/executed and the actual Top 10 result recorded.

---

# 24. Co-Occurrence Source

Current files:

```text
src\coOccurrence\CoOccurrence.java
src\coOccurrence\CoOccurrenceMapper.java
src\coOccurrence\CoOccurrenceReducer.java
```

JAR:

```text
E:\Big-Data-Mapper-Reducer\cooccurrence.jar
```

Current implementation generates adjacent word pairs.

Example:

```text
machine learning is powerful
```

produces:

```text
machine learning
learning is
is powerful
```

---

# 25. Co-Occurrence Compilation

Recommended:

```cmd
E:
cd E:\Big-Data-Mapper-Reducer
```

Then:

```cmd
javac -classpath "%HADOOP_HOME%\share\hadoop\common\*;%HADOOP_HOME%\share\hadoop\common\lib\*;%HADOOP_HOME%\share\hadoop\hdfs\*;%HADOOP_HOME%\share\hadoop\hdfs\lib\*;%HADOOP_HOME%\share\hadoop\mapreduce\*;%HADOOP_HOME%\share\hadoop\mapreduce\lib\*;%HADOOP_HOME%\share\hadoop\yarn\*;%HADOOP_HOME%\share\hadoop\yarn\lib\*" -d bin src\coOccurrence\*.java
```

Verify:

```cmd
dir bin\coOccurrence
```

Expected:

```text
CoOccurrence.class
CoOccurrenceMapper.class
CoOccurrenceReducer.class
```

Create JAR:

```cmd
jar -cvf cooccurrence.jar -C bin .
```

---

# 26. Previous Co-Occurrence Compilation Error

Incorrect:

```cmd
javac -d bin -cp "...classpath..." E:\Big-Data-Mapper-Reducer\src\coOccurrence
```

Reason: `javac` needs source files, not just the directory.

Correct:

```cmd
E:
cd E:\Big-Data-Mapper-Reducer

javac -d bin -classpath "...classpath..." src\coOccurrence\*.java
```

---

# 27. IMPORTANT: Co-Occurrence Needs One Logic Change

The original repository does **not** simply count every adjacent pair.

Its README specifies that Co-Occurrence is calculated for the **Top 10 words found by Word Count**.

Original concept:

```text
Word Count
    |
    v
Top 10 Words
    |
    v
Co-Occurrence Mapper
    |
    +--> Is current word in Top 10?
    |
    +--> Find adjacent word
    |
    v
<Word, Adjacent Word>, 1
    |
    v
Reducer
    |
    v
<Word, Adjacent Word>, Frequency
```

Our current Mapper generates adjacent pairs for all words.

Therefore the next important coding task is:

**Modify `CoOccurrenceMapper.java` to use the actual Top 10 words from Word Count.**

---

# 28. Co-Occurrence Test

Do not immediately run the full dataset.

Create:

```cmd
hdfs dfs -mkdir -p /BigData/CommonCrawlTest
```

Upload a few files:

```cmd
hdfs dfs -put data\processed\CommonCrawlData\CleanedArticleBooks1.txt /BigData/CommonCrawlTest/
hdfs dfs -put data\processed\CommonCrawlData\CleanedArticleBooks2.txt /BigData/CommonCrawlTest/
hdfs dfs -put data\processed\CommonCrawlData\CleanedArticleBooks3.txt /BigData/CommonCrawlTest/
```

Check:

```cmd
hdfs dfs -ls /BigData/CommonCrawlTest
```

Remove old test output:

```cmd
hdfs dfs -rm -r /BigData/CoOccurrenceTest
```

Run:

```cmd
hadoop jar cooccurrence.jar coOccurrence.CoOccurrence /BigData/CommonCrawlTest /BigData/CoOccurrenceTest
```

Check:

```cmd
hdfs dfs -ls /BigData/CoOccurrenceTest
```

View:

```cmd
hdfs dfs -cat /BigData/CoOccurrenceTest/part-r-00000
```

Only after the test works should the full dataset be processed.

---

# 29. Full Co-Occurrence

After the Mapper is corrected:

```cmd
hdfs dfs -rm -r /BigData/CommonCrawlCoOccurrence
```

Run:

```cmd
hadoop jar cooccurrence.jar coOccurrence.CoOccurrence /BigData/CommonCrawlData /BigData/CommonCrawlCoOccurrence
```

Check:

```cmd
hdfs dfs -ls /BigData/CommonCrawlCoOccurrence
```

View:

```cmd
hdfs dfs -cat /BigData/CommonCrawlCoOccurrence/part-r-00000
```

---

# 30. Performance / Monitoring

The full Common Crawl Word Count job previously took a significant amount of time.

Do not assume a job is stuck only because progress is slow.

Monitor:

```cmd
yarn application -list
```

```cmd
yarn application -status <APPLICATION_ID>
```

```cmd
yarn node -list
```

Web UI:

```text
http://localhost:8088
```

The UI can confirm whether a job is:

```text
RUNNING
FINISHED
FAILED
KILLED
```

---

# 31. Internet Requirement

Once data is already local/HDFS:

**MapReduce does not require internet.**

Internet is only needed for things such as:

- downloading datasets
- GitHub access
- package installation
- external APIs
- external web services

The actual Hadoop MapReduce computation runs locally.

---

# 32. Original Repository Scope

The original README says the project used approximately:

- 20,000 tweets
- 500 New York Times articles
- 500 Common Crawl articles

The entertainment topic was divided into:

```text
Movies
Games
Music
Books
Television
```

The original data sources are:

```text
Twitter
New York Times
Common Crawl
```

---

# 33. Twitter — NOT YET IMPLEMENTED

Original project used Tweepy.

It filtered:

- English tweets
- non-retweets
- entertainment-related hashtags

Our current implementation has not added Twitter collection.

The original repository contains historical API credentials in notebooks. **Do not reuse them.** If Twitter/X collection is required, use newly configured credentials.

---

# 34. New York Times — NOT YET IMPLEMENTED

Original project used:

```text
NYT Article API
BeautifulSoup
```

Pipeline:

```text
NYT API
   |
   v
Article URLs
   |
   v
BeautifulSoup
   |
   v
<p> text
   |
   v
Article files
```

Our current implementation has not added NYT collection.

Do not reuse historical API keys from the original repository.

---

# 35. Common Crawl — CURRENT FOCUS

Common Crawl is already implemented far enough to perform:

```text
Raw data
  ↓
Cleaning
  ↓
HDFS
  ↓
Word Count
```

The remaining Common Crawl work is:

```text
Top 10
  ↓
Top-10-based Co-Occurrence
  ↓
Analysis
  ↓
Visualization
```

---

# 36. Data Quality Note

Raw Common Crawl data can contain:

- navigation text
- login pages
- advertisements
- JavaScript text
- social media labels
- HTML remnants
- unrelated web content

This is expected from web-crawled data.

The current cleaner reduces some noise but is not a complete semantic/web-page extraction system.

---

# 37. Python Analysis — NOT YET COMPLETED

Planned analysis directory:

```text
analysis```

Possible files:

```text
analysis├── top_words.py
├── word_cloud.py
├── analyze_cooccurrence.py
└── results```

Planned tasks:

1. Read Word Count output
2. Sort frequencies
3. Find Top 10
4. Analyze co-occurrence
5. Generate charts
6. Generate word clouds
7. Save final images

---

# 38. Visualization — NOT YET COMPLETED

Original project uses Tableau.

Final visualization can include:

- Top 10 words
- Word Cloud
- Co-Occurrence frequency
- Comparisons between sources

For exact reproduction, the original project has six main output groups:

```text
Twitter Word Count
Twitter Co-Occurrence

NYT Word Count
NYT Co-Occurrence

Common Crawl Word Count
Common Crawl Co-Occurrence
```

Our current project only has the Common Crawl branch.

---

# 39. Final Target Architecture

```text
                 DATA COLLECTION
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
    Twitter          NYT        Common Crawl
       |              |              |
       +--------------+--------------+
                      |
                      v
              DATA PREPROCESSING
                      |
                      v
                    HDFS
                      |
          +-----------+-----------+
          |                       |
          v                       v
      WORD COUNT           CO-OCCURRENCE
          |                       |
          v                       |
       TOP 10 <-------------------+
          |
          v
       ANALYSIS
          |
          v
   WORD CLOUD / TABLEAU
          |
          v
     FINAL INSIGHTS
```

---

# 40. Current Completion Status

## DONE

### Machine

- Windows
- Java 8
- Hadoop 3.3.6
- HDFS
- YARN
- MapReduce

### Project

- Project directory
- VS Code configuration
- Source structure
- Raw Common Crawl
- Data cleaning
- Processed Common Crawl
- HDFS upload

### Word Count

- Mapper
- Reducer
- Driver
- Compilation
- JAR
- HDFS execution
- Successful MapReduce job
- `_SUCCESS`
- `part-r-00000`
- Local `output\wordcount.txt`

## IN PROGRESS

- Top 10 execution
- Co-Occurrence compilation/testing
- Co-Occurrence algorithm correction

## NOT YET DONE

- Top-10-based Co-Occurrence full execution
- Python analysis
- Word Cloud
- Tableau
- Twitter
- NYT
- Combined three-source analysis
- Final trend analysis
- Final project report

---

# 41. Remaining Tasks — Recommended Order

```text
1. Finish TopNWords.java
        ↓
2. Get actual Top 10 words
        ↓
3. Modify CoOccurrenceMapper
   to use Top 10
        ↓
4. Compile Co-Occurrence
        ↓
5. Build cooccurrence.jar
        ↓
6. Test on 2–3 files
        ↓
7. Run full Common Crawl Co-Occurrence
        ↓
8. Analyze Word Count + Co-Occurrence
        ↓
9. Generate visualizations
        ↓
10. Optional Tableau
        ↓
11. Optional Twitter + NYT
        ↓
12. Final report/documentation
```

---

# 42. Important Paths Cheat Sheet

| Purpose | Path |
|---|---|
| Main project | `E:\Big-Data-Mapper-Reducer` |
| Raw Common Crawl | `E:\Big-Data-Mapper-Reducer\data\raw\CommonCrawlData` |
| Processed Common Crawl | `E:\Big-Data-Mapper-Reducer\data\processed\CommonCrawlData` |
| Java source | `E:\Big-Data-Mapper-Reducer\src` |
| Processing | `E:\Big-Data-Mapper-Reducer\src\processing` |
| Word Count | `E:\Big-Data-Mapper-Reducer\src\wordCount` |
| Co-Occurrence | `E:\Big-Data-Mapper-Reducer\src\coOccurrence` |
| Compiled classes | `E:\Big-Data-Mapper-Reducer\bin` |
| Word Count JAR | `E:\Big-Data-Mapper-Reducer\wc.jar` |
| Co-Occurrence JAR | `E:\Big-Data-Mapper-Reducer\cooccurrence.jar` |
| Local output | `E:\Big-Data-Mapper-Reducer\output` |
| Word Count local output | `E:\Big-Data-Mapper-Reducer\output\wordcount.txt` |
| Hadoop | `C:\hadoop-3.3.6` |
| Java | `C:\Java\jdk-8.0.492.9-hotspot` |
| ResourceManager | `http://localhost:8088` |
| NameNode | `http://localhost:9870` |

---

# 43. HDFS Paths Cheat Sheet

| Purpose | HDFS Path |
|---|---|
| Common Crawl input | `/BigData/CommonCrawlData` |
| Word Count output | `/BigData/CommonCrawlWordCount` |
| Small Co-Occurrence input | `/BigData/CommonCrawlTest` |
| Small Co-Occurrence output | `/BigData/CoOccurrenceTest` |
| Full Co-Occurrence output | `/BigData/CommonCrawlCoOccurrence` |

---

# 44. Most Important Commands

Enter project:

```cmd
E:
cd E:\Big-Data-Mapper-Reducer
```

Start Hadoop:

```cmd
start-dfs.cmd
start-yarn.cmd
```

Check YARN:

```cmd
yarn node -list
```

Check applications:

```cmd
yarn application -list
```

Check HDFS:

```cmd
hdfs dfs -ls /
```

Upload cleaned data:

```cmd
hdfs dfs -put data\processed\CommonCrawlData\* /BigData/CommonCrawlData/
```

Run Word Count:

```cmd
hadoop jar wc.jar wordCount.WordCount /BigData/CommonCrawlData /BigData/CommonCrawlWordCount
```

Copy Word Count output:

```cmd
hdfs dfs -get /BigData/CommonCrawlWordCount/part-r-00000 output\wordcount.txt
```

View Word Count output:

```cmd
hdfs dfs -cat /BigData/CommonCrawlWordCount/part-r-00000
```

Remove old Word Count output:

```cmd
hdfs dfs -rm -r /BigData/CommonCrawlWordCount
```

---

# 45. Troubleshooting Rules

## Output directory already exists

```cmd
hdfs dfs -rm -r /BigData/<output-directory>
```

then rerun.

## javac says directory/source error

Use:

```cmd
src\coOccurrence\*.java
```

instead of:

```cmd
src\coOccurrence
```

## Relative paths behave incorrectly

Check:

```cmd
cd
```

Then:

```cmd
E:
cd E:\Big-Data-Mapper-Reducer
```

## YARN has zero nodes

Check:

```cmd
yarn node -list
```

Then inspect:

```text
http://localhost:8088
```

and restart YARN if necessary:

```cmd
stop-yarn.cmd
start-yarn.cmd
```

## NodeManager becomes unhealthy

A previous known issue was:

```text
local-dirs usable space is below configured utilization percentage
```

This means the NodeManager local directory exceeded the configured disk-utilization threshold.

Check free disk space and Hadoop local directories before rerunning large jobs.

---

# 46. Historical Hadoop Issues

The machine previously encountered:

```text
Address already in use: bind
```

and NodeManager registration/local-directory problems.

At one point NodeManager reported:

```text
UNHEALTHY
```

because its local directory was above the configured 90% utilization threshold.

These are Hadoop runtime/storage issues, not necessarily Java source-code problems.

When debugging, distinguish:

```text
Java compilation error
```

from:

```text
Hadoop/YARN runtime error
```

from:

```text
HDFS input/output error
```

---

# 47. Git Repository

Current repository:

```text
https://github.com/pruthal2309/Big-Data-Analysis-using-MapReduce.git
```

Original reference:

```text
https://github.com/Mgosi/Big-Data-Analysis-using-MapReduce-in-Hadoop
```

---

# 48. Git Commands

From:

```cmd
E:
cd E:\Big-Data-Mapper-Reducer
```

Check:

```cmd
git status
git branch
git remote -v
```

Commit:

```cmd
git add .
git commit -m "Update MapReduce project"
```

Push:

```cmd
git push -u origin main
```

If:

```text
src refspec main does not match any
```

check:

```cmd
git status
git log --oneline
git branch
```

---

# 49. Rules for Anyone Continuing the Project

Before giving a new command, check:

1. Current working directory
2. Java version
3. Hadoop version
4. `JAVA_HOME`
5. `HADOOP_HOME`
6. Whether HDFS/YARN is running
7. Whether the HDFS output directory already exists
8. Whether source package/folder names match
9. Whether the JAR needs rebuilding
10. Whether the command is for local Windows or HDFS

Always distinguish:

### Local Windows path

```text
E:\Big-Data-Mapper-Reducer\data\processed\CommonCrawlData
```

### HDFS path

```text
/BigData/CommonCrawlData
```

These are different systems and paths.

---

# 50. Current Project Status — One View

```text
MACHINE
================================================
Windows                         DONE
Java 8                          DONE
Hadoop 3.3.6                    DONE
HDFS                            DONE
YARN                            DONE
MapReduce                       DONE


PROJECT
================================================
Project setup                  DONE
VS Code setup                  DONE
Raw Common Crawl               DONE
Data cleaning                  DONE
Processed Common Crawl         DONE
HDFS upload                    DONE
WordCount Mapper               DONE
WordCount Reducer              DONE
WordCount Driver               DONE
WordCount JAR                  DONE
WordCount MapReduce            DONE
WordCount HDFS output          DONE
Local wordcount.txt            DONE

Top 10 Words                   IN PROGRESS
Co-Occurrence code             IN PROGRESS
Top-10-based Co-Occurrence     NOT DONE
Full Co-Occurrence             NOT DONE
Python analysis                NOT DONE
Word Cloud                     NOT DONE
Tableau                        NOT DONE
Twitter                        NOT DONE
NYT                            NOT DONE
Final report                   NOT DONE
```

---

# 51. Immediate Next Task

The next task should **not** be reinstalling Hadoop.

The machine and Hadoop setup are already working.

The next development sequence is:

```text
output\wordcount.txt
        ↓
Top 10 Words
        ↓
Modify CoOccurrenceMapper
        ↓
Top-10-based Co-Occurrence
        ↓
Test on 2–3 files
        ↓
Full Common Crawl
        ↓
Python Analysis
        ↓
Visualization
```

This context should be updated whenever major project paths, versions, completed tasks, commands, HDFS locations, or remaining tasks change.
