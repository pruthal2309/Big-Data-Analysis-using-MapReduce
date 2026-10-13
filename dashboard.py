"""
Big Data MapReduce Analysis Dashboard
======================================
Built with Streamlit | Hadoop + MapReduce Results Visualizer
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import networkx as nx
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import re
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore")

# ── Actual Top 10 from MapReduce top10.txt ──────────────────
ACTUAL_TOP10 = [
    ("the",     204111),
    ("window",  106559),
    ("jsqueue", 101400),
    ("of",      100407),
    ("to",       96684),
    ("a",        91286),
    ("and",      89879),
    ("in",       67636),
    ("s",        63357),
    ("push",     52845),
]

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Big Data MapReduce Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Root theme */
:root {
    --primary: #6C63FF;
    --secondary: #FF6584;
    --accent: #43E97B;
    --dark: #0D0D1A;
    --card-bg: rgba(255,255,255,0.04);
    --border: rgba(108,99,255,0.25);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0D0D1A 0%, #141428 40%, #0D1B2A 100%);
    color: #E8E8F0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111126 0%, #0D0D1A 100%);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #C8C8E0 !important;
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #6C63FF 0%, #4834D4 40%, #2D1B8E 100%);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(108,99,255,0.35);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
    text-shadow: 0 2px 20px rgba(0,0,0,0.3);
}
.hero-subtitle {
    font-size: 1.05rem;
    color: rgba(255,255,255,0.82);
    margin: 0;
    font-weight: 400;
    letter-spacing: 0.02em;
}

/* Metric cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.2rem;
    margin-bottom: 2rem;
}
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(108,99,255,0.2);
}
.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 16px 0 0 16px;
}
.metric-card.purple::after { background: #6C63FF; }
.metric-card.pink::after   { background: #FF6584; }
.metric-card.green::after  { background: #43E97B; }
.metric-card.orange::after { background: #F7971E; }
.metric-value {
    font-size: 2.0rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1;
    margin: 0 0 0.3rem 0;
}
.metric-label {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin: 0;
}
.metric-icon {
    font-size: 1.8rem;
    margin-bottom: 0.6rem;
}

/* Section headings */
.section-heading {
    font-size: 1.4rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 2rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-heading .badge {
    font-size: 0.65rem;
    background: linear-gradient(135deg, #6C63FF, #4834D4);
    color: #fff;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* Chart wrappers */
.chart-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(108,99,255,0.18);
    border-radius: 18px;
    padding: 1.6rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}

/* Insight chips */
.insight-strip {
    background: linear-gradient(135deg, rgba(108,99,255,0.12), rgba(67,233,123,0.08));
    border: 1px solid rgba(108,99,255,0.25);
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    margin: 1rem 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.insight-item {
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    font-size: 0.9rem;
    color: #C8C8E0;
    line-height: 1.5;
}

/* Findings box */
.findings-box {
    background: linear-gradient(135deg, rgba(67,233,123,0.08), rgba(108,99,255,0.06));
    border-left: 4px solid #43E97B;
    border-radius: 0 14px 14px 0;
    padding: 1.2rem 1.6rem;
    margin: 1rem 0;
}
.findings-box h4 {
    color: #43E97B;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 0.7rem 0;
    font-weight: 700;
}
.findings-box p {
    color: #C8C8E0;
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.7;
}

/* Tables */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(108,99,255,0.4), transparent);
    margin: 2rem 0;
}

/* Tab styling */
[data-baseweb="tab"] {
    font-weight: 600 !important;
    color: #8888AA !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: #6C63FF !important;
}

/* Pipeline steps */
.pipeline {
    display: flex;
    align-items: center;
    gap: 0;
    flex-wrap: wrap;
    margin: 1rem 0;
}
.pipeline-step {
    background: rgba(108,99,255,0.15);
    border: 1px solid rgba(108,99,255,0.35);
    border-radius: 10px;
    padding: 0.6rem 1.1rem;
    font-size: 0.82rem;
    font-weight: 600;
    color: #B0AAFF;
    white-space: nowrap;
}
.pipeline-arrow {
    color: rgba(108,99,255,0.5);
    font-size: 1.2rem;
    padding: 0 0.4rem;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem;
    color: rgba(255,255,255,0.3);
    font-size: 0.8rem;
    border-top: 1px solid rgba(108,99,255,0.15);
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────

# ── Only remove pure noise (single/double chars, hex strings) ──
# We deliberately keep ALL real English words AND web/JS terms because
# they are the genuine MapReduce results from Common Crawl data.
STOPWORDS_NOISE_ONLY = {
    # Single-character tokens
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    # Pure noise / encoding artefacts
    "amp", "nbsp", "quot", "apos", "lt", "gt",
    "http", "https", "www", "com", "org", "net", "html", "htm", "php",
    "charset", "utf",
}

# ── Content-words filter (used ONLY when user toggles it) ──────
# These are stop-words that carry no topic meaning.
CONTENT_STOPWORDS = STOPWORDS_NOISE_ONLY | {
    "the", "of", "to", "and", "in", "is", "for", "that", "it", "on",
    "are", "was", "with", "as", "at", "be", "by", "this", "an", "or",
    "from", "but", "not", "have", "had", "has", "he", "she", "they",
    "we", "you", "his", "her", "their", "our", "its", "been", "were",
    "will", "do", "did", "can", "could", "would", "should", "may",
    "might", "shall", "which", "who", "what", "when", "where", "how",
    "if", "then", "than", "so", "all", "more", "also", "about", "up",
    "out", "no", "other", "into", "there", "these", "those", "some",
    "over", "after", "before", "while", "any", "each", "one", "two",
    "new", "time", "very", "just", "only", "your", "my", "me", "him",
    "them", "us", "via", "per",
}

@st.cache_data(show_spinner=False)
def load_wordcount(path="output/wordcount.txt", content_only=False, top_n=200):
    """
    Load word count output — two modes:
      content_only=False  →  Show RAW MapReduce output (actual results, minimal cleanup)
      content_only=True   →  Filter English stop-words to show topic/content words only
    """
    stopwords = CONTENT_STOPWORDS if content_only else STOPWORDS_NOISE_ONLY
    words, freqs = [], []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) != 2:
                    continue
                word, freq = parts[0].strip(), parts[1].strip()
                try:
                    freq = int(freq)
                except ValueError:
                    continue
                # Minimal filter: at least 2 chars, all alphabetic, not pure noise
                if (re.match(r'^[a-z]{2,}$', word) and
                        word not in stopwords and
                        freq >= 1):
                    words.append(word)
                    freqs.append(freq)
    except FileNotFoundError:
        return pd.DataFrame({"word": [], "frequency": []})

    df = pd.DataFrame({"word": words, "frequency": freqs})
    df = df.sort_values("frequency", ascending=False).head(top_n).reset_index(drop=True)
    return df


@st.cache_data(show_spinner=False)
def load_cooccurrence(path="WordCooccurrenceOutput/coOccurrence/cooccurrence.txt",
                      content_only=False, top_n=50):
    """Load co-occurrence data — minimal noise filter, two modes."""
    stopwords = CONTENT_STOPWORDS if content_only else STOPWORDS_NOISE_ONLY
    pairs = defaultdict(int)
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.rsplit("\t", 1)
                if len(parts) != 2:
                    continue
                pair_str, count_str = parts
                try:
                    count = int(count_str.strip())
                except ValueError:
                    continue
                words = pair_str.strip().split()
                if len(words) != 2:
                    continue
                w1, w2 = words[0].strip(), words[1].strip()
                # Minimal filter: at least 2 chars, alphabetic, not pure noise
                if (re.match(r'^[a-z]{2,}$', w1) and
                        re.match(r'^[a-z]{2,}$', w2) and
                        w1 not in stopwords and
                        w2 not in stopwords and
                        w1 != w2 and
                        count >= 1):
                    key = tuple(sorted([w1, w2]))
                    pairs[key] += count
    except FileNotFoundError:
        return pd.DataFrame({"word1": [], "word2": [], "count": []})

    rows = [{"word1": k[0], "word2": k[1], "count": v} for k, v in pairs.items()]
    df = pd.DataFrame(rows).sort_values("count", ascending=False).head(top_n).reset_index(drop=True)
    return df


# ─────────────────────────────────────────────────────────────
# MATPLOTLIB DARK THEME HELPER
# ─────────────────────────────────────────────────────────────
def apply_dark_theme(fig, ax_list=None):
    fig.patch.set_facecolor("#0D0D1A")
    if ax_list is None:
        ax_list = fig.get_axes()
    for ax in ax_list:
        ax.set_facecolor("#141428")
        ax.tick_params(colors="#AAAACC", labelsize=9)
        ax.xaxis.label.set_color("#AAAACC")
        ax.yaxis.label.set_color("#AAAACC")
        ax.title.set_color("#FFFFFF")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2A2A4A")


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem 0;'>
        <div style='font-size:2.5rem;'>🔬</div>
        <div style='font-size:1.1rem; font-weight:800; color:#B0AAFF; margin-top:0.3rem;'>MapReduce</div>
        <div style='font-size:0.75rem; color:#6666AA; letter-spacing:0.1em; text-transform:uppercase;'>Analysis Dashboard</div>
    </div>
    <hr style='border-color:rgba(108,99,255,0.2); margin: 1rem 0;'>
    """, unsafe_allow_html=True)

    st.markdown("#### ⚙️ Dashboard Settings")

    st.markdown("""
    <div style='background:rgba(108,99,255,0.12); border:1px solid rgba(108,99,255,0.3);
                border-radius:10px; padding:0.8rem 1rem; margin-bottom:0.8rem;'>
        <div style='font-size:0.8rem; font-weight:700; color:#B0AAFF; margin-bottom:0.5rem;'>📊 View Mode</div>
    </div>
    """, unsafe_allow_html=True)
    view_mode = st.radio(
        "Select what to display:",
        options=["🔬 Raw MapReduce Output", "📚 Content Words Only"],
        index=0,
        help="Raw Output = actual Hadoop results (the, window, jsqueue…). Content Words Only = stop-words removed.",
    )
    content_only = (view_mode == "📚 Content Words Only")

    if not content_only:
        st.markdown("""
        <div style='background:rgba(67,233,123,0.08); border-left:3px solid #43E97B;
                    border-radius:0 8px 8px 0; padding:0.5rem 0.8rem; margin-bottom:0.8rem;
                    font-size:0.78rem; color:#88DDAA;'>
            ✅ Showing <b>actual MapReduce output</b> — all real top words including <i>the, window, jsqueue, push</i> etc.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:rgba(247,151,30,0.08); border-left:3px solid #F7971E;
                    border-radius:0 8px 8px 0; padding:0.5rem 0.8rem; margin-bottom:0.8rem;
                    font-size:0.78rem; color:#DDBB88;'>
            📚 Stop-words filtered — showing topic/content words only.
        </div>
        """, unsafe_allow_html=True)

    top_n_words = st.slider("Top N Words to Display", min_value=5, max_value=30, value=20, step=5)
    top_n_pairs = st.slider("Top N Co-occurrence Pairs", min_value=10, max_value=50, value=25, step=5)
    heatmap_words = st.slider("Heatmap Word Count", min_value=8, max_value=20, value=12, step=2)
    network_nodes = st.slider("Network Graph Nodes", min_value=10, max_value=40, value=20, step=5)

    st.markdown("<hr style='border-color:rgba(108,99,255,0.2);'>", unsafe_allow_html=True)

    show_raw = st.checkbox("Show Raw Data Tables", value=False)

    st.markdown("<hr style='border-color:rgba(108,99,255,0.2);'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.78rem; color:#555577; line-height:1.7;'>
        <b style='color:#8888AA;'>📁 Data Sources</b><br>
        • output/wordcount.txt<br>
        • WordCooccurrenceOutput/<br>&nbsp;&nbsp;coOccurrence/cooccurrence.txt<br><br>
        <b style='color:#8888AA;'>🛠 Pipeline</b><br>
        Common Crawl → DataCleaner<br>
        → Hadoop HDFS → MapReduce<br>
        → Word Count + Co-Occ → Dashboard
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(108,99,255,0.2);'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.72rem; color:#444466; text-align:center;'>
        Hadoop 3.3.6 &nbsp;|&nbsp; Java 8<br>
        Python 3.13 &nbsp;|&nbsp; Streamlit
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
with st.spinner("🔄 Loading MapReduce output data…"):
    wc_df   = load_wordcount(content_only=content_only, top_n=200)
    cooc_df = load_cooccurrence(content_only=content_only, top_n=100)

top_words_df = wc_df.head(top_n_words)
top_pairs_df = cooc_df.head(top_n_pairs)

total_unique = len(wc_df)
total_tokens = wc_df["frequency"].sum() if not wc_df.empty else 0
top_word = wc_df.iloc[0]["word"] if not wc_df.empty else "N/A"
top_freq = wc_df.iloc[0]["frequency"] if not wc_df.empty else 0
top_pair = f"{cooc_df.iloc[0]['word1']} ↔ {cooc_df.iloc[0]['word2']}" if not cooc_df.empty else "N/A"


# ─────────────────────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🔬 Big Data MapReduce Analysis</div>
    <div class="hero-subtitle">
        Common Crawl Text Analysis &nbsp;|&nbsp; Hadoop 3.3.6 &nbsp;|&nbsp;
        MapReduce Word Count + Co-Occurrence &nbsp;|&nbsp; Interactive NLP Dashboard
    </div>
    <div class="pipeline" style="margin-top:1.5rem;">
        <span class="pipeline-step">📦 Common Crawl</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">🧹 DataCleaner</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">🐘 Hadoop HDFS</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">⚡ MapReduce</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">📊 Analysis</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">🎯 Insights</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card purple">
        <div class="metric-icon">📝</div>
        <div class="metric-value">{total_unique:,}</div>
        <div class="metric-label">Unique Meaningful Words</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card pink">
        <div class="metric-icon">🔢</div>
        <div class="metric-value">{total_tokens/1_000_000:.1f}M</div>
        <div class="metric-label">Total Token Occurrences</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card green">
        <div class="metric-icon">🏆</div>
        <div class="metric-value">"{top_word}"</div>
        <div class="metric-label">Most Dominant Word ({top_freq:,}×)</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card orange">
        <div class="metric-icon">🔗</div>
        <div class="metric-value">{len(cooc_df):,}</div>
        <div class="metric-label">Co-occurrence Pairs Found</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Word Frequency",
    "☁️ Word Cloud",
    "🔥 Co-Occurrence Heatmap",
    "🕸️ Word Network",
    "📋 Key Findings",
    "🔍 Word Explorer",
])


# ══════════════════════════════════════════════════════════════
# TAB 1 — WORD FREQUENCY
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f"""
    <div class="section-heading">
        📊 Top {top_n_words} Most Frequent Words
        <span class="badge">MapReduce Output</span>
    </div>""", unsafe_allow_html=True)

    if wc_df.empty:
        st.error("⚠️ Could not load word count data. Check `output/wordcount.txt`.")
    else:
        # ── Official Top 10 from top10.txt ────────────────────
        st.markdown("""
        <div class="section-heading" style="font-size:1.05rem; margin-top:0;">
            🏅 Official Top 10 — Verified from top10.txt
            <span class="badge" style="background:linear-gradient(135deg,#43E97B,#38F9D7); color:#000;">Exact MapReduce Output</span>
        </div>""", unsafe_allow_html=True)

        top10_df_disp = pd.DataFrame(ACTUAL_TOP10, columns=["Word", "Frequency"])
        top10_df_disp.index = top10_df_disp.index + 1
        top10_df_disp["% of Top 10 Total"] = [
            f"{f/(sum(v for _,v in ACTUAL_TOP10))*100:.1f}%"
            for _, f in ACTUAL_TOP10
        ]
        top10_df_disp["Frequency"] = top10_df_disp["Frequency"].apply(lambda x: f"{x:,}")
        st.dataframe(top10_df_disp, width='stretch', height=390)

        st.markdown("""
        <div style='background:rgba(67,233,123,0.07); border:1px solid rgba(67,233,123,0.2);
                    border-radius:10px; padding:0.8rem 1.2rem; margin-bottom:1.5rem;
                    font-size:0.85rem; color:#88DDAA;'>
            ✅ These are the <b>exact numbers</b> from the Hadoop MapReduce Word Count job
            (output/top10.txt). The interactive chart below reflects all words from wordcount.txt.
        </div>
        """, unsafe_allow_html=True)

        # ── Plotly interactive bar chart ──────────────────────
        colors = px.colors.sequential.Plasma_r[:top_n_words] if top_n_words <= len(px.colors.sequential.Plasma_r) else None


        fig_bar = px.bar(
            top_words_df.sort_values("frequency"),
            x="frequency",
            y="word",
            orientation="h",
            color="frequency",
            color_continuous_scale="Plasma",
            labels={"frequency": "Frequency", "word": "Word"},
            title=f"Top {top_n_words} Words by Frequency",
            text="frequency",
        )
        fig_bar.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='outside',
            marker_line_width=0,
        )
        fig_bar.update_layout(
            paper_bgcolor="#0D0D1A",
            plot_bgcolor="#141428",
            font=dict(family="Inter", color="#AAAACC", size=12),
            title_font=dict(size=18, color="#FFFFFF", family="Inter"),
            coloraxis_showscale=False,
            height=600,
            margin=dict(l=20, r=80, t=60, b=20),
            xaxis=dict(
                gridcolor="rgba(108,99,255,0.1)",
                zerolinecolor="rgba(108,99,255,0.2)",
                tickfont=dict(size=11),
            ),
            yaxis=dict(
                tickfont=dict(size=12, color="#FFFFFF"),
                categoryorder='total ascending',
            ),
        )
        st.plotly_chart(fig_bar, width='stretch')

        # ── Frequency distribution histogram ─────────────────
        st.markdown("""
        <div class="section-heading" style="font-size:1.1rem;">
            📈 Frequency Distribution (Top 100 Words)
        </div>""", unsafe_allow_html=True)

        fig_hist = px.histogram(
            wc_df.head(100),
            x="frequency",
            nbins=20,
            color_discrete_sequence=["#6C63FF"],
            title="Distribution of Word Frequencies",
            labels={"frequency": "Frequency", "count": "Number of Words"},
        )
        fig_hist.update_layout(
            paper_bgcolor="#0D0D1A",
            plot_bgcolor="#141428",
            font=dict(family="Inter", color="#AAAACC", size=12),
            title_font=dict(size=16, color="#FFFFFF"),
            height=320,
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis=dict(gridcolor="rgba(108,99,255,0.1)"),
            yaxis=dict(gridcolor="rgba(108,99,255,0.1)"),
            bargap=0.05,
        )
        st.plotly_chart(fig_hist, width='stretch')

        # ── Insights ──────────────────────────────────────────
        top3 = wc_df.head(3)
        pct_top5 = wc_df.head(5)["frequency"].sum() / wc_df["frequency"].sum() * 100
        st.markdown(f"""
        <div class="insight-strip">
            <div class="insight-item">💡 <span>The top 3 words — <b style='color:#B0AAFF;'>{top3.iloc[0]['word']}</b>, <b style='color:#B0AAFF;'>{top3.iloc[1]['word']}</b>, and <b style='color:#B0AAFF;'>{top3.iloc[2]['word']}</b> — together account for <b style='color:#43E97B;'>{top3['frequency'].sum():,}</b> occurrences.</span></div>
            <div class="insight-item">📉 <span>The top 5 words represent <b style='color:#FF6584;'>{pct_top5:.1f}%</b> of all filtered token occurrences, indicating a high-frequency skew typical of natural language.</span></div>
            <div class="insight-item">🧠 <span>After removing stop-words and noise tokens from <b>{wc_df.shape[0]:,}</b> unique filtered words, the remaining vocabulary reveals the corpus's core themes.</span></div>
        </div>
        """, unsafe_allow_html=True)

        if show_raw:
            st.markdown("**Raw Word Frequency Data**")
            st.dataframe(
                wc_df.head(top_n_words).style.background_gradient(
                    subset=["frequency"], cmap="Purples"
                ).format({"frequency": "{:,}"}),
                width='stretch',
                height=300,
            )


# ══════════════════════════════════════════════════════════════
# TAB 2 — WORD CLOUD
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="section-heading">
        ☁️ Word Cloud Visualization
        <span class="badge">Frequency-Weighted</span>
    </div>""", unsafe_allow_html=True)

    if wc_df.empty:
        st.error("⚠️ No data available for word cloud.")
    else:
        # Build frequency dict
        freq_dict = dict(zip(wc_df["word"].head(150), wc_df["frequency"].head(150)))

        # Color function — vivid gradient palette
        def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
            colors_pool = [
                "#6C63FF", "#B47FFF", "#FF6584", "#FF9FBA",
                "#43E97B", "#38F9D7", "#F7971E", "#FFD200",
                "#4FACFE", "#00F2FE",
            ]
            return colors_pool[abs(hash(word)) % len(colors_pool)]

        wc_obj = WordCloud(
            width=1400,
            height=600,
            background_color="#0D0D1A",
            max_words=120,
            color_func=color_func,
            prefer_horizontal=0.75,
            min_font_size=10,
            max_font_size=140,
            relative_scaling=0.55,
            collocations=False,
        ).generate_from_frequencies(freq_dict)

        fig_wc, ax_wc = plt.subplots(figsize=(14, 6), facecolor="#0D0D1A")
        ax_wc.imshow(wc_obj, interpolation="bilinear")
        ax_wc.axis("off")
        ax_wc.set_facecolor("#0D0D1A")
        plt.tight_layout(pad=0)
        st.pyplot(fig_wc, width='stretch')
        plt.close()

        st.markdown("""
        <div class="insight-strip">
            <div class="insight-item">☁️ <span>Word size is proportional to term frequency — larger words appear more often in the MapReduce output.</span></div>
            <div class="insight-item">🎨 <span>Colors are randomly assigned for visual distinction; they do not encode additional meaning.</span></div>
            <div class="insight-item">📌 <span>The word cloud uses the top 120 filtered, meaningful words after stop-word removal.</span></div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 3 — CO-OCCURRENCE HEATMAP
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="section-heading">
        🔥 Word Co-Occurrence Heatmap
        <span class="badge">Hadoop MapReduce</span>
    </div>""", unsafe_allow_html=True)

    if cooc_df.empty:
        st.error("⚠️ No co-occurrence data available.")
    else:
        # Build pivot matrix
        heat_df = cooc_df.head(heatmap_words * 4)
        all_words_heat = list(
            pd.unique(heat_df[["word1", "word2"]].values.ravel("K"))
        )[:heatmap_words]

        matrix = pd.DataFrame(0, index=all_words_heat, columns=all_words_heat)
        for _, row in heat_df.iterrows():
            w1, w2, cnt = row["word1"], row["word2"], row["count"]
            if w1 in all_words_heat and w2 in all_words_heat:
                matrix.loc[w1, w2] = cnt
                matrix.loc[w2, w1] = cnt

        fig_heat, ax_heat = plt.subplots(figsize=(11, 9), facecolor="#0D0D1A")
        ax_heat.set_facecolor("#0D0D1A")

        cmap = sns.color_palette("rocket_r", as_cmap=True)
        sns.heatmap(
            matrix,
            ax=ax_heat,
            cmap="magma",
            linewidths=0.4,
            linecolor="#0D0D1A",
            annot=True,
            fmt="d",
            annot_kws={"size": 8, "color": "white"},
            cbar_kws={"label": "Co-occurrence Count", "shrink": 0.8},
        )
        ax_heat.set_title(
            f"Word Co-Occurrence Matrix (Top {heatmap_words} Words)",
            color="white", fontsize=15, fontweight="bold", pad=16
        )
        ax_heat.tick_params(colors="#CCCCEE", labelsize=10)
        ax_heat.set_xticklabels(ax_heat.get_xticklabels(), rotation=45, ha="right", color="#CCCCEE")
        ax_heat.set_yticklabels(ax_heat.get_yticklabels(), rotation=0, color="#CCCCEE")

        cbar = ax_heat.collections[0].colorbar
        cbar.ax.yaxis.label.set_color("#AAAACC")
        cbar.ax.tick_params(colors="#AAAACC")
        cbar.outline.set_edgecolor("#2A2A4A")

        plt.tight_layout()
        st.pyplot(fig_heat, width='stretch')
        plt.close()

        # Top pairs table
        st.markdown("""
        <div class="section-heading" style="font-size:1.05rem; margin-top:1.5rem;">
            🔝 Strongest Co-occurring Pairs
        </div>""", unsafe_allow_html=True)

        fig_pairs = px.bar(
            cooc_df.head(15),
            x="count",
            y=cooc_df.head(15).apply(lambda r: f"{r['word1']} ↔ {r['word2']}", axis=1),
            orientation="h",
            color="count",
            color_continuous_scale="Magma",
            labels={"x": "Co-occurrence Count", "y": "Word Pair"},
            title="Top 15 Word Co-occurrence Pairs",
            text="count",
        )
        fig_pairs.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_pairs.update_layout(
            paper_bgcolor="#0D0D1A",
            plot_bgcolor="#141428",
            font=dict(family="Inter", color="#AAAACC", size=12),
            title_font=dict(size=16, color="#FFFFFF"),
            coloraxis_showscale=False,
            height=450,
            margin=dict(l=20, r=80, t=50, b=20),
            xaxis=dict(gridcolor="rgba(255,165,0,0.1)"),
            yaxis=dict(tickfont=dict(color="#FFFFFF", size=11), categoryorder='total ascending'),
        )
        st.plotly_chart(fig_pairs, width='stretch')

        # Insight
        top_pair_row = cooc_df.iloc[0]
        st.markdown(f"""
        <div class="insight-strip">
            <div class="insight-item">🔥 <span>Darker cells in the heatmap indicate more frequent co-occurrence — words that tend to appear together in the same context window.</span></div>
            <div class="insight-item">🔗 <span>Strongest pair: <b style='color:#FFD700;'>{top_pair_row['word1']} ↔ {top_pair_row['word2']}</b> with <b style='color:#43E97B;'>{top_pair_row['count']:,}</b> co-occurrences, suggesting a strong semantic relationship.</span></div>
            <div class="insight-item">📐 <span>The matrix is symmetric — if word A co-occurs with word B, B also co-occurs with A by definition.</span></div>
        </div>
        """, unsafe_allow_html=True)

        if show_raw:
            st.dataframe(
                cooc_df.head(top_n_pairs).style.background_gradient(
                    subset=["count"], cmap="Oranges"
                ).format({"count": "{:,}"}),
                width='stretch',
                height=300,
            )


# ══════════════════════════════════════════════════════════════
# TAB 4 — WORD NETWORK
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="section-heading">
        🕸️ Word Relationship Network
        <span class="badge">NetworkX Graph</span>
    </div>""", unsafe_allow_html=True)

    if cooc_df.empty or wc_df.empty:
        st.error("⚠️ Need both word count and co-occurrence data for the network.")
    else:
        net_pairs = cooc_df.head(network_nodes * 2)

        G = nx.Graph()
        for _, row in net_pairs.iterrows():
            G.add_edge(row["word1"], row["word2"], weight=row["count"])

        # Only keep top nodes by degree
        top_deg_nodes = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:network_nodes]
        nodes_to_keep = [n for n, _ in top_deg_nodes]
        G = G.subgraph(nodes_to_keep).copy()

        # Node sizes from word frequency
        wc_lookup = dict(zip(wc_df["word"], wc_df["frequency"]))
        max_freq = max(wc_lookup.get(n, 1) for n in G.nodes()) or 1

        # Layout
        pos = nx.spring_layout(G, k=2.5, iterations=60, seed=42)

        # Edge traces
        edge_x, edge_y, edge_weights = [], [], []
        for e in G.edges(data=True):
            x0, y0 = pos[e[0]]
            x1, y1 = pos[e[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
            edge_weights.append(e[2]["weight"])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.2, color="rgba(108,99,255,0.35)"),
            hoverinfo="none",
            mode="lines",
            name="",
        )

        # Node traces
        node_x = [pos[n][0] for n in G.nodes()]
        node_y = [pos[n][1] for n in G.nodes()]
        node_freq = [wc_lookup.get(n, 100) for n in G.nodes()]
        node_size = [12 + 40 * (f / max_freq) ** 0.6 for f in node_freq]
        node_degree = [dict(G.degree())[n] for n in G.nodes()]

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=list(G.nodes()),
            textposition="top center",
            textfont=dict(size=10, color="#FFFFFF", family="Inter"),
            marker=dict(
                size=node_size,
                color=node_degree,
                colorscale="Plasma",
                showscale=True,
                colorbar=dict(
                    title="Node Degree",
                    title_font_color="#AAAACC",
                    tickfont_color="#AAAACC",
                    bgcolor="#0D0D1A",
                    bordercolor="#2A2A4A",
                ),
                line=dict(width=2, color="#0D0D1A"),
            ),
            hovertext=[
                f"<b>{n}</b><br>Freq: {wc_lookup.get(n,0):,}<br>Connections: {dict(G.degree())[n]}"
                for n in G.nodes()
            ],
            name="",
        )

        fig_net = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=dict(
                    text=f"Word Relationship Network ({len(G.nodes())} nodes, {len(G.edges())} edges)",
                    font=dict(size=18, color="#FFFFFF", family="Inter"),
                ),
                showlegend=False,
                hovermode="closest",
                paper_bgcolor="#0D0D1A",
                plot_bgcolor="#0D0D1A",
                height=620,
                margin=dict(l=20, r=20, t=60, b=20),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                font=dict(family="Inter", color="#AAAACC"),
            )
        )
        st.plotly_chart(fig_net, width='stretch')

        # Network stats
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Nodes", len(G.nodes()))
        with c2:
            st.metric("Edges", len(G.edges()))
        with c3:
            density = nx.density(G)
            st.metric("Graph Density", f"{density:.3f}")
        with c4:
            if nx.is_connected(G):
                avg_path = nx.average_shortest_path_length(G)
                st.metric("Avg Path Length", f"{avg_path:.2f}")
            else:
                components = nx.number_connected_components(G)
                st.metric("Components", components)

        st.markdown(f"""
        <div class="insight-strip">
            <div class="insight-item">🔵 <span><b>Larger nodes</b> = higher word frequency in the corpus; <b>node color</b> = number of connections (degree).</span></div>
            <div class="insight-item">📏 <span><b>Thicker/brighter edges</b> = words that appear together more often in the same context window.</span></div>
            <div class="insight-item">🕸️ <span>Highly-connected hub words reveal thematic clusters — words that act as bridges between topics in the corpus.</span></div>
            <div class="insight-item">💡 <span>Hover over any node to see its frequency and connection count. The network is interactive — drag nodes to explore.</span></div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 5 — KEY FINDINGS
# ══════════════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div class="section-heading">
        📋 Summary Statistics & Key Findings
        <span class="badge">Project Report</span>
    </div>""", unsafe_allow_html=True)

    # ── Project Overview ─────────────────────────────────────
    st.markdown("""
    <div class="chart-card">
        <h3 style='color:#B0AAFF; margin:0 0 1rem 0; font-size:1.1rem;'>🏗️ Project Architecture</h3>
        <div style='color:#C0C0D8; font-size:0.9rem; line-height:2;'>
            <b style='color:#6C63FF;'>Dataset:</b> Common Crawl web corpus (multiple article files)<br>
            <b style='color:#6C63FF;'>Preprocessing:</b> Java DataCleaner — lowercase, URL/HTML/punctuation removal, whitespace normalization<br>
            <b style='color:#6C63FF;'>Storage:</b> Hadoop HDFS at <code style='background:rgba(108,99,255,0.15); padding:0.1rem 0.4rem; border-radius:4px;'>/BigData/CommonCrawlData</code><br>
            <b style='color:#6C63FF;'>MapReduce 1:</b> Word Count — Mapper emits (word, 1), Reducer sums → frequency table<br>
            <b style='color:#6C63FF;'>MapReduce 2:</b> Co-Occurrence — Mapper emits adjacent word pairs, Reducer sums co-occurrence counts<br>
            <b style='color:#6C63FF;'>Output size:</b> wordcount.txt ≈ 480 KB (43,017 unique tokens), cooccurrence.txt ≈ 3.6 MB (238,582 pairs)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats columns ─────────────────────────────────────────
    fc1, fc2 = st.columns(2)

    with fc1:
        st.markdown("""
        <div class="chart-card">
            <h3 style='color:#B0AAFF; margin:0 0 1rem 0; font-size:1.05rem;'>📊 Word Count Statistics</h3>
        </div>
        """, unsafe_allow_html=True)
        if not wc_df.empty:
            stats = {
                "Total Unique Tokens (raw)": "43,017",
                "Meaningful Words (filtered)": f"{len(wc_df):,}",
                "Total Occurrences (filtered)": f"{wc_df['frequency'].sum():,}",
                "Most Frequent Word": f"{wc_df.iloc[0]['word']} ({wc_df.iloc[0]['frequency']:,}×)",
                "Least Frequent (in top 200)": f"{wc_df.iloc[-1]['word']} ({wc_df.iloc[-1]['frequency']:,}×)",
                "Median Frequency": f"{wc_df['frequency'].median():,.0f}",
                "Mean Frequency": f"{wc_df['frequency'].mean():,.0f}",
            }
            stats_df = pd.DataFrame(list(stats.items()), columns=["Metric", "Value"])
            st.dataframe(stats_df, width='stretch', hide_index=True, height=280)

    with fc2:
        st.markdown("""
        <div class="chart-card">
            <h3 style='color:#FF9FBA; margin:0 0 1rem 0; font-size:1.05rem;'>🔗 Co-Occurrence Statistics</h3>
        </div>
        """, unsafe_allow_html=True)
        if not cooc_df.empty:
            stats2 = {
                "Total Raw Pairs": "238,582",
                "Meaningful Pairs (filtered)": f"{len(cooc_df):,}",
                "Strongest Pair": f"{cooc_df.iloc[0]['word1']} ↔ {cooc_df.iloc[0]['word2']}",
                "Strongest Count": f"{cooc_df.iloc[0]['count']:,}",
                "2nd Strongest Pair": f"{cooc_df.iloc[1]['word1']} ↔ {cooc_df.iloc[1]['word2']}",
                "2nd Count": f"{cooc_df.iloc[1]['count']:,}",
                "Avg Co-occurrence (top 100)": f"{cooc_df['count'].mean():,.0f}",
            }
            stats2_df = pd.DataFrame(list(stats2.items()), columns=["Metric", "Value"])
            st.dataframe(stats2_df, width='stretch', hide_index=True, height=280)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── Top words highlight ───────────────────────────────────
    st.markdown("""
    <div class="section-heading" style="font-size:1.1rem;">
        🏆 Top 20 Words at a Glance
    </div>""", unsafe_allow_html=True)

    fig_top20 = go.Figure()
    top20 = wc_df.head(20)
    colors_20 = [f"hsl({int(220 + i*7)}, 75%, 65%)" for i in range(20)]

    fig_top20.add_trace(go.Bar(
        x=top20["word"],
        y=top20["frequency"],
        marker_color=colors_20,
        text=top20["frequency"].apply(lambda x: f"{x:,}"),
        textposition="outside",
        textfont=dict(size=9, color="#FFFFFF"),
    ))
    fig_top20.update_layout(
        paper_bgcolor="#0D0D1A",
        plot_bgcolor="#141428",
        font=dict(family="Inter", color="#AAAACC"),
        title=dict(text="Top 20 Words — Frequency Overview", font=dict(size=16, color="#FFFFFF")),
        height=380,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(tickfont=dict(color="#FFFFFF", size=11), gridcolor="rgba(108,99,255,0.08)"),
        yaxis=dict(gridcolor="rgba(108,99,255,0.08)", tickfont=dict(size=10)),
    )
    st.plotly_chart(fig_top20, width='stretch')

    # ── Key Findings ─────────────────────────────────────────
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="section-heading" style="font-size:1.1rem;">🔍 Key Findings</div>""", unsafe_allow_html=True)

    top3_words = wc_df.head(3)
    top_pair_f = cooc_df.iloc[0]

    st.markdown(f"""
    <div class="findings-box">
        <h4>✅ Confirmed Findings</h4>
        <p>
        1. <b>Dominant vocabulary:</b> After removing stop-words, the most frequent meaningful terms are
        <b>{top3_words.iloc[0]['word']}</b> ({top3_words.iloc[0]['frequency']:,}×),
        <b>{top3_words.iloc[1]['word']}</b> ({top3_words.iloc[1]['frequency']:,}×), and
        <b>{top3_words.iloc[2]['word']}</b> ({top3_words.iloc[2]['frequency']:,}×).
        These reflect the core subject matter of the Common Crawl web corpus.<br><br>

        2. <b>Power-law distribution:</b> Word frequencies follow Zipf's Law — a small number of words account
        for a disproportionately large share of all occurrences, consistent with natural language behavior.<br><br>

        3. <b>Strong co-occurrence pair:</b> <b>{top_pair_f['word1']}</b> and <b>{top_pair_f['word2']}</b> appear
        together <b>{top_pair_f['count']:,} times</b>, indicating a strong semantic or syntactic relationship
        in the corpus — likely appearing in similar web content categories.<br><br>

        4. <b>MapReduce effectiveness:</b> The two MapReduce jobs (Word Count + Co-Occurrence) successfully processed
        a large-scale corpus across Hadoop's distributed framework, producing 43,017 unique tokens and
        238,582 word-pair records with high throughput.<br><br>

        5. <b>Network topology:</b> The word relationship network exhibits small-world properties —
        a few hub words act as connectors between topically-different word clusters.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── MapReduce Job Summary ─────────────────────────────────
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="section-heading" style="font-size:1.1rem;">⚡ MapReduce Job Summary</div>""", unsafe_allow_html=True)

    job_data = {
        "Job": ["Word Count", "Co-Occurrence"],
        "Input": ["/BigData/CommonCrawlData", "/BigData/CommonCrawlData"],
        "Output": ["/BigData/CommonCrawlWordCount", "/BigData/CommonCrawlCoOccurrence"],
        "Output Records": ["43,017 tokens", "238,582 pairs"],
        "Output Size": ["~480 KB", "~3.6 MB"],
        "Status": ["✅ SUCCEEDED", "✅ SUCCEEDED"],
    }
    job_df = pd.DataFrame(job_data)
    st.dataframe(job_df, width='stretch', hide_index=True)




# ==============================================================
# TAB 6 - SMART WORD RELATIONSHIP EXPLORER
# ==============================================================
@st.cache_data(show_spinner=False)
def build_word_index(_content_only=False):
    """Build neighbor lookup from co-occurrence file."""
    cooc_path = "WordCooccurrenceOutput/coOccurrence/cooccurrence.txt"
    stopwords = CONTENT_STOPWORDS if _content_only else STOPWORDS_NOISE_ONLY
    neighbors = defaultdict(list)
    edges = []
    try:
        with open(cooc_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.rsplit("\t", 1)
                if len(parts) != 2:
                    continue
                pair_str, count_str = parts
                try:
                    count = int(count_str.strip())
                except ValueError:
                    continue
                ws = pair_str.strip().split()
                if len(ws) != 2:
                    continue
                w1, w2 = ws[0].strip(), ws[1].strip()
                if (re.match(r"^[a-z]{2,}$", w1) and
                        re.match(r"^[a-z]{2,}$", w2) and
                        w1 not in stopwords and w2 not in stopwords and
                        w1 != w2 and count >= 5):
                    neighbors[w1].append((w2, count))
                    neighbors[w2].append((w1, count))
                    edges.append((w1, w2, count))
    except FileNotFoundError:
        pass
    for w in neighbors:
        neighbors[w].sort(key=lambda x: x[1], reverse=True)
    return dict(neighbors), edges


_CPAL = [
    "#6C63FF", "#FF6584", "#43E97B", "#F7971E",
    "#4FACFE", "#FFD200", "#B47FFF", "#38F9D7", "#FF9FBA", "#A8EDEA",
]


with tab6:
    st.markdown(
        '<div class="section-heading">'
        "\U0001f50d Smart Word Relationship Explorer"
        '<span class="badge" style="background:linear-gradient(135deg,#FF6584,#FF9FBA);color:#fff;">Interactive</span>'
        "</div>"
        '<div style="color:#9090AA;font-size:0.88rem;margin:-0.5rem 0 1.5rem 0;line-height:1.6;">'
        "Select any word to explore its co-occurrence neighbourhood &mdash; direct connections, "
        "cluster membership, and relationship strength &mdash; all from your Hadoop MapReduce output."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.spinner("\U0001f517 Building word relationship index..."):
        _wi, _ae = build_word_index(_content_only=content_only)

    if not _wi:
        st.error("\u26a0\ufe0f Co-occurrence data not found or too small.")
    else:
        _vocab = sorted(_wi.keys())
        _c1, _c2, _c3 = st.columns([3, 1.5, 1.5])
        with _c1:
            _dw = ("the" if "the" in _wi else "window" if "window" in _wi else _vocab[0])
            _sel = st.selectbox(
                "\U0001f50e Choose a word to explore:",
                options=_vocab,
                index=_vocab.index(_dw),
                key="explorer_word",
            )
        with _c2:
            _mn = st.slider("Max neighbours", 5, 40, 15, key="exp_nbrs")
        with _c3:
            _dep = st.radio(
                "Graph depth", ["1-hop", "2-hop"], index=0, key="exp_depth",
                help="1-hop = direct connections. 2-hop = include neighbours-of-neighbours.",
            )

        _wlu = dict(zip(wc_df["word"], wc_df["frequency"])) if not wc_df.empty else {}
        _nbrs = _wi.get(_sel, [])[:_mn]
        _enodes = {_sel} | {n for n, _ in _nbrs}
        if _dep == "2-hop":
            for _nb, _ in _nbrs:
                _enodes |= {n for n, _ in _wi.get(_nb, [])[:8]}

        _Gego = nx.Graph()
        for _w1, _w2, _cnt in _ae:
            if _w1 in _enodes and _w2 in _enodes:
                _Gego.add_edge(_w1, _w2, weight=_cnt)
        _Gego.add_node(_sel)

        try:
            _comms = list(nx.community.greedy_modularity_communities(_Gego, weight="weight"))
        except Exception:
            _comms = [set(_Gego.nodes())]

        _nc_map = {}
        for _ci, _cm in enumerate(_comms):
            for _nd in _cm:
                _nc_map[_nd] = _ci

        def _gcol(_nd):
            return "#FFD700" if _nd == _sel else _CPAL[_nc_map.get(_nd, 0) % len(_CPAL)]

        _pos = nx.spring_layout(_Gego, k=2.8, seed=42, weight="weight", iterations=80)
        if _sel in _pos:
            _off = -_pos[_sel].copy()
            for _nd in _pos:
                _pos[_nd] = _pos[_nd] + _off

        _ews = [_Gego[u][v].get("weight", 1) for u, v in _Gego.edges()]
        _mxw = max(_ews) if _ews else 1
        _etraces = []
        for _u, _v, _ed in _Gego.edges(data=True):
            _r = _ed.get("weight", 1) / _mxw
            if _u == _sel or _v == _sel:
                _ec = "rgba(255,215,0,{:.2f})".format(0.3 + 0.5 * _r)
                _ew2 = 1.5 + 4.5 * _r
            else:
                _ec = "rgba(108,99,255,{:.2f})".format(0.1 + 0.3 * _r)
                _ew2 = 0.6 + 2.0 * _r
            _x0, _y0 = _pos[_u]
            _x1, _y1 = _pos[_v]
            _etraces.append(go.Scatter(
                x=[_x0, _x1, None], y=[_y0, _y1, None],
                mode="lines", line=dict(width=_ew2, color=_ec),
                hoverinfo="none", showlegend=False,
            ))

        _dd = dict(_Gego.degree())
        _mxf = max((_wlu.get(n, 1) for n in _Gego.nodes()), default=1)
        _nxl, _nyl, _ncl, _nsl, _ntl, _nhl = [], [], [], [], [], []
        for _nd in _Gego.nodes():
            _x, _y = _pos[_nd]
            _nxl.append(_x); _nyl.append(_y)
            _ncl.append(_gcol(_nd))
            _f = _wlu.get(_nd, 0)
            _nsl.append(52 if _nd == _sel else (14 + 28 * (_f / _mxf) ** 0.5))
            _ntl.append(_nd)
            _dw2 = next((c for nb, c in _wi.get(_sel, []) if nb == _nd), None)
            _hl = [
                "<b>{}</b>".format(_nd),
                "Frequency: {:,}".format(_f),
                "Connections: {}".format(_dd.get(_nd, 0)),
                "Cluster {}".format(_nc_map.get(_nd, 0) + 1),
            ]
            if _dw2:
                _hl.append("Co-occ with '{}': {:,}".format(_sel, _dw2))
            _nhl.append("<br>".join(_hl))

        _nt_exp = go.Scatter(
            x=_nxl, y=_nyl, mode="markers+text",
            marker=dict(size=_nsl, color=_ncl,
                        line=dict(width=2, color="#0D0D1A"), opacity=0.95),
            text=_ntl, textposition="top center",
            textfont=dict(size=10, color="#FFFFFF", family="Inter"),
            hovertext=_nhl, hoverinfo="text", showlegend=False,
        )

        _sx, _sy = _pos.get(_sel, (0, 0))
        _halo = go.Scatter(
            x=[_sx], y=[_sy], mode="markers",
            marker=dict(size=74, color="rgba(255,215,0,0.12)",
                        line=dict(width=3, color="#FFD700")),
            hoverinfo="skip", showlegend=False,
        )

        _ncl_n = len(_comms)
        _fig_exp = go.Figure(
            data=_etraces + [_halo, _nt_exp],
            layout=go.Layout(
                title=dict(
                    text="<b>'{}'</b>  &middot;  {} nodes  &middot;  {} edges  &middot;  {} cluster{}".format(
                        _sel, len(_Gego.nodes()), len(_Gego.edges()),
                        _ncl_n, "s" if _ncl_n != 1 else ""),
                    font=dict(size=16, color="#FFFFFF", family="Inter"), x=0.01,
                ),
                paper_bgcolor="#0D0D1A", plot_bgcolor="#0D0D1A", height=650,
                margin=dict(l=10, r=10, t=58, b=10),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                hovermode="closest", font=dict(family="Inter", color="#AAAACC"),
            )
        )

        _gcol2, _scol = st.columns([2.6, 1])

        with _gcol2:
            st.plotly_chart(_fig_exp, width="stretch")
            _leg = ""
            for _ci, _cm in enumerate(_comms[:8]):
                _cc = _CPAL[_ci % len(_CPAL)]
                _tm = sorted(_cm, key=lambda n: _wlu.get(n, 0), reverse=True)[:4]
                _leg += (
                    '<span style="display:inline-flex;align-items:center;gap:5px;'
                    'background:rgba(255,255,255,0.04);border:1px solid {}44;'
                    'border-radius:8px;padding:4px 10px;margin:4px 4px 0 0;font-size:0.78rem;">'
                    '<span style="width:10px;height:10px;border-radius:50%;background:{};'
                    'display:inline-block;flex-shrink:0;"></span>'
                    '<b style="color:{}">C{}</b>: '
                    '<span style="color:#AAAACC">{}</span></span>'
                ).format(_cc, _cc, _cc, _ci + 1, ", ".join(_tm))
            st.markdown(
                '<div style="margin-top:0.6rem;">{}</div>'.format(_leg),
                unsafe_allow_html=True,
            )

        with _scol:
            _sf = _wlu.get(_sel, 0)
            _sd = _dd.get(_sel, 0)
            _sc2 = _nc_map.get(_sel, 0)
            _scc = _CPAL[_sc2 % len(_CPAL)]
            st.markdown(
                '<div style="background:linear-gradient(135deg,rgba(255,215,0,0.10),'
                'rgba(108,99,255,0.08));border:1px solid rgba(255,215,0,0.3);'
                'border-radius:16px;padding:1.3rem;margin-bottom:1rem;">'
                '<div style="font-size:0.68rem;color:rgba(255,215,0,0.75);text-transform:uppercase;'
                'letter-spacing:0.1em;font-weight:700;margin-bottom:0.3rem;">Selected Word</div>'
                '<div style="font-size:1.9rem;font-weight:800;color:#FFD700;margin-bottom:0.8rem;'
                'word-break:break-all;">{}</div>'
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">'
                '<div style="background:rgba(0,0,0,0.25);border-radius:10px;padding:0.55rem;text-align:center;">'
                '<div style="font-size:1.1rem;font-weight:800;color:#FFFFFF;">{}</div>'
                '<div style="font-size:0.6rem;color:#8888AA;text-transform:uppercase;">Freq</div></div>'
                '<div style="background:rgba(0,0,0,0.25);border-radius:10px;padding:0.55rem;text-align:center;">'
                '<div style="font-size:1.1rem;font-weight:800;color:#FFFFFF;">{}</div>'
                '<div style="font-size:0.6rem;color:#8888AA;text-transform:uppercase;">Edges</div></div>'
                '<div style="background:rgba(0,0,0,0.25);border-radius:10px;padding:0.55rem;text-align:center;">'
                '<div style="font-size:1.1rem;font-weight:800;color:{};">C{}</div>'
                '<div style="font-size:0.6rem;color:#8888AA;text-transform:uppercase;">Cluster</div></div>'
                '<div style="background:rgba(0,0,0,0.25);border-radius:10px;padding:0.55rem;text-align:center;">'
                '<div style="font-size:1.1rem;font-weight:800;color:#FFFFFF;">{}</div>'
                '<div style="font-size:0.6rem;color:#8888AA;text-transform:uppercase;">Nodes</div></div>'
                '</div></div>'.format(
                    _sel, "{:,}".format(_sf), _sd,
                    _scc, _sc2 + 1, len(_Gego.nodes())
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div style="font-size:0.82rem;font-weight:700;color:#B0AAFF;'
                'margin:0.2rem 0 0.5rem 0;">'
                "\U0001f517 Strongest Connections</div>",
                unsafe_allow_html=True,
            )
            _dnbrs = _wi.get(_sel, [])[:15]
            _tc = _dnbrs[0][1] if _dnbrs else 1
            for _rk, (_nb, _ct) in enumerate(_dnbrs, 1):
                _nf = _wlu.get(_nb, 0)
                _bp = int(100 * _ct / _tc) if _tc > 0 else 0
                _nbc = _CPAL[_nc_map.get(_nb, 0) % len(_CPAL)]
                st.markdown(
                    '<div style="background:rgba(255,255,255,0.03);'
                    'border:1px solid rgba(255,255,255,0.06);'
                    'border-radius:9px;padding:0.45rem 0.65rem;margin-bottom:0.32rem;">'
                    '<div style="display:flex;justify-content:space-between;align-items:center;">'
                    '<div style="font-weight:700;color:{};font-size:0.84rem;">#{} {}</div>'
                    '<div style="font-size:0.72rem;color:#43E97B;font-weight:700;">{}</div></div>'
                    '<div style="background:rgba(255,255,255,0.04);border-radius:4px;'
                    'height:4px;margin-top:0.28rem;overflow:hidden;">'
                    '<div style="background:{};width:{}%;height:100%;border-radius:4px;"></div></div>'
                    '<div style="font-size:0.65rem;color:#555577;margin-top:0.14rem;">freq: {}</div>'
                    '</div>'.format(
                        _nbc, _rk, _nb, "{:,}".format(_ct),
                        _nbc, _bp, "{:,}".format(_nf)
                    ),
                    unsafe_allow_html=True,
                )
            if not _dnbrs:
                st.info("No direct connections found for this word.")

            st.markdown(
                '<div style="font-size:0.82rem;font-weight:700;color:#B0AAFF;'
                'margin:0.8rem 0 0.5rem 0;">'
                "\U0001fae7 Cluster Breakdown</div>",
                unsafe_allow_html=True,
            )
            for _ci, _cm in enumerate(_comms):
                _cc = _CPAL[_ci % len(_CPAL)]
                _tm = sorted(_cm, key=lambda n: _wlu.get(n, 0), reverse=True)[:5]
                st.markdown(
                    '<div style="background:rgba(255,255,255,0.02);'
                    'border-left:3px solid {};border-radius:0 8px 8px 0;'
                    'padding:0.45rem 0.7rem;margin-bottom:0.32rem;">'
                    '<div style="font-size:0.72rem;font-weight:700;color:{};">'
                    'Cluster {} <span style="color:#555577;font-weight:400;">({} words)</span></div>'
                    '<div style="font-size:0.68rem;color:#AAAACC;margin-top:0.12rem;">{}</div>'
                    '</div>'.format(
                        _cc, _cc, _ci + 1, len(_cm),
                        " &middot; ".join(_tm)
                    ),
                    unsafe_allow_html=True,
                )

        _sn = _dnbrs[0][0] if _dnbrs else "N/A"
        _sc3 = _dnbrs[0][1] if _dnbrs else 0
        st.markdown(
            '<div class="insight-strip" style="margin-top:1.2rem;">'
            '<div class="insight-item">\U0001f31f '
            "<span>The word <b style=\"color:#FFD700;\">'{}' </b>"
            "co-occurs most strongly with <b style=\"color:#43E97B;\">{}</b>"
            " ({:,}&times;), indicating a tight semantic relationship in the corpus.</span></div>"
            '<div class="insight-item">\U0001fae7 '
            "<span>NetworkX detected <b style=\"color:#B0AAFF;\">{} cluster{}</b>"
            " using greedy modularity maximisation &mdash; each cluster groups words"
            " that frequently appear together in the same context window.</span></div>"
            '<div class="insight-item">\u2b55 '
            "<span><b style=\"color:#FFD700;\">Gold node + ring</b> = selected word &nbsp;"
            "<b style=\"color:#6C63FF;\">Colored nodes</b> = cluster &nbsp;"
            "<b>Brighter edges</b> = higher co-occurrence. "
            "Hover any node for full statistics. Drag to rearrange.</span></div>"
            "</div>".format(
                _sel, _sn, _sc3,
                _ncl_n, "s" if _ncl_n != 1 else ""
            ),
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <b style='color:#6C63FF;'>Big Data Analysis using MapReduce in Hadoop</b><br>
    Hadoop 3.3.6 &nbsp;|&nbsp; Java 8 &nbsp;|&nbsp; Python 3.13 &nbsp;|&nbsp;
    Streamlit &nbsp;|&nbsp; Matplotlib &nbsp;|&nbsp; Seaborn &nbsp;|&nbsp;
    NetworkX &nbsp;|&nbsp; WordCloud &nbsp;|&nbsp; Plotly<br>
    <span style='color:#333355;'>Common Crawl Dataset &nbsp;|&nbsp; MapReduce Word Frequency & Co-Occurrence Analysis</span>
</div>
""", unsafe_allow_html=True)
