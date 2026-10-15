"""
Test script to verify Spark ML integration with MapReduce outputs
Run this to check if Phase 2 is working correctly
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("=" * 60)
    print("Testing imports...")
    print("=" * 60)
    
    try:
        import pandas
        print("✅ pandas")
    except ImportError:
        print("❌ pandas - run: pip install pandas")
        return False
    
    try:
        import numpy
        print("✅ numpy")
    except ImportError:
        print("❌ numpy - run: pip install numpy")
        return False
    
    try:
        import spark_ml
        print("✅ spark_ml module")
    except ImportError:
        print("❌ spark_ml.py not found")
        return False
    
    # PySpark is optional
    if spark_ml.is_available():
        print("✅ PySpark")
        return True
    else:
        print("⚠️  PySpark not installed (optional)")
        print("   Install with: pip install pyspark")
        return False


def test_data_files():
    """Check that MapReduce output files exist"""
    print("\n" + "=" * 60)
    print("Checking MapReduce output files...")
    print("=" * 60)
    
    files_to_check = [
        "output/wordcount.txt",
        "WordCooccurrenceOutput/coOccurrence/cooccurrence.txt"
    ]
    
    all_exist = True
    for filepath in files_to_check:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✅ {filepath} ({size:,} bytes)")
        else:
            print(f"❌ {filepath} - NOT FOUND")
            all_exist = False
    
    return all_exist


def test_spark_session():
    """Test Spark session creation and summary"""
    print("\n" + "=" * 60)
    print("Testing Spark session...")
    print("=" * 60)
    
    try:
        import spark_ml
        
        if not spark_ml.is_available():
            print("⚠️  PySpark not available - skipping Spark tests")
            return False
        
        summary = spark_ml.get_spark_summary()
        
        print(f"✅ Spark session created")
        print(f"   Version: {summary.get('spark_version', 'N/A')}")
        print(f"   Master: {summary.get('master', 'N/A')}")
        print(f"   Status: {summary.get('status', 'N/A')}")
        print(f"   Word count records: {summary.get('wc_records', 0):,}")
        print(f"   Co-occurrence records: {summary.get('cooc_records', 0):,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Spark session failed: {e}")
        return False


def test_tfidf():
    """Test TF-IDF pipeline"""
    print("\n" + "=" * 60)
    print("Testing TF-IDF pipeline...")
    print("=" * 60)
    
    try:
        import spark_ml
        
        if not spark_ml.is_available():
            print("⚠️  Skipping (PySpark not available)")
            return False
        
        print("Running TF-IDF on top 30 words...")
        result = spark_ml.run_tfidf(top_n=30, num_features=128)
        
        if "error" in result.columns:
            print(f"❌ TF-IDF failed: {result['error'].iloc[0]}")
            return False
        
        print(f"✅ TF-IDF completed successfully")
        print(f"   Processed {len(result)} words")
        print(f"\n   Top 5 by TF-IDF score:")
        for idx, row in result.head(5).iterrows():
            print(f"   {idx+1}. {row['word']:15s} - {row['tfidf_score']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ TF-IDF test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_kmeans():
    """Test K-Means clustering"""
    print("\n" + "=" * 60)
    print("Testing K-Means clustering...")
    print("=" * 60)
    
    try:
        import spark_ml
        
        if not spark_ml.is_available():
            print("⚠️  Skipping (PySpark not available)")
            return False
        
        print("Running K-Means with k=4 on top 50 words...")
        result = spark_ml.run_kmeans(k=4, top_n=50)
        
        if "error" in result.columns:
            print(f"❌ K-Means failed: {result['error'].iloc[0]}")
            return False
        
        print(f"✅ K-Means completed successfully")
        print(f"   Clustered {len(result)} words into 4 groups")
        
        cluster_counts = result['cluster'].value_counts().sort_index()
        print(f"\n   Cluster distribution:")
        for cluster_id, count in cluster_counts.items():
            print(f"   Cluster {cluster_id}: {count} words")
        
        return True
        
    except Exception as e:
        print(f"❌ K-Means test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lda():
    """Test LDA topic modeling"""
    print("\n" + "=" * 60)
    print("Testing LDA topic modeling...")
    print("=" * 60)
    
    try:
        import spark_ml
        
        if not spark_ml.is_available():
            print("⚠️  Skipping (PySpark not available)")
            return False
        
        print("Running LDA with 3 topics on top 50 words...")
        result = spark_ml.run_lda(num_topics=3, top_n_words=50, top_words_per_topic=5)
        
        topics_df = result.get("topics")
        word_topics_df = result.get("word_topics")
        
        if topics_df is None or "error" in topics_df.columns:
            print(f"❌ LDA failed")
            return False
        
        print(f"✅ LDA completed successfully")
        print(f"   Discovered {len(topics_df)} topics")
        print(f"   Analyzed {len(word_topics_df)} words")
        
        print(f"\n   Topics preview:")
        for idx, row in topics_df.iterrows():
            print(f"   Topic {row['topic_id']}: {row['top_words']}")
        
        return True
        
    except Exception as e:
        print(f"❌ LDA test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  SPARK ML INTEGRATION TEST SUITE".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60 + "\n")
    
    results = {
        "Imports": test_imports(),
        "Data Files": test_data_files(),
        "Spark Session": test_spark_session(),
        "TF-IDF": test_tfidf(),
        "K-Means": test_kmeans(),
        "LDA": test_lda(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s} {status}")
    
    total = len(results)
    passed_count = sum(1 for p in results.values() if p)
    
    print("=" * 60)
    print(f"Total: {passed_count}/{total} tests passed")
    print("=" * 60)
    
    if passed_count == total:
        print("\n🎉 All tests passed! Spark ML integration is working perfectly.")
        print("   Run 'streamlit run dashboard.py' to see it in action.")
    elif results.get("Imports") and results.get("Data Files"):
        print("\n⚠️  Core components working, but Spark ML needs setup.")
        print("   Install PySpark: pip install pyspark")
        print("   Then re-run this test.")
    else:
        print("\n❌ Some critical components failed.")
        print("   Check the errors above and fix them.")
    
    return passed_count == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
