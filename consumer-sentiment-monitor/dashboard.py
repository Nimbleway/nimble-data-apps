"""Streamlit dashboard for Consumer Sentiment Monitor runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
SAMPLE_RUN = DATA_DIR / "sample_run"


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def find_runs() -> List[Path]:
    runs = []
    for base in (DATA_DIR / "runs", DATA_DIR):
        if not base.exists():
            continue
        for report in base.glob("*/report.json"):
            runs.append(report.parent)
    if SAMPLE_RUN.exists():
        runs.append(SAMPLE_RUN)
    return sorted(set(runs), key=lambda p: (p / "report.json").stat().st_mtime if (p / "report.json").exists() else 0, reverse=True)


def source_link(url: str) -> str:
    if not url:
        return ""
    return f"[source]({url})"


st.set_page_config(page_title="Consumer Sentiment Monitor", page_icon="📡", layout="wide")
st.title("📡 Consumer Sentiment Monitor")
st.caption("Nimble Search API → launch sentiment report → source-linked dashboard")

runs = find_runs()
if not runs:
    st.error("No runs found. Run `python3 collect.py --dry-run` first.")
    st.stop()

run_labels = [str(p.relative_to(APP_DIR)) for p in runs]
selected = st.sidebar.selectbox("Run", run_labels, index=0)
run_dir = APP_DIR / selected
report = load_json(run_dir / "report.json")
normalized_path = run_dir / "normalized_results.json"
normalized = load_json(normalized_path) if normalized_path.exists() else report.get("representative_examples", [])

st.sidebar.markdown("### Run files")
st.sidebar.code(str(run_dir))
st.sidebar.markdown("Run a fresh dry-run:")
st.sidebar.code("python3 collect.py --dry-run")

summary = report.get("executive_summary", {})
metrics = report.get("metrics", {})
product = report.get("product_name", "Product")
st.subheader(product)
st.write(report.get("launch_context", ""))

c1, c2, c3, c4 = st.columns(4)
sentiment_counts = metrics.get("sentiment_counts", {})
c1.metric("Overall", str(summary.get("overall_sentiment", "mixed")).title())
c2.metric("Results", metrics.get("total_results", 0))
c3.metric("Positive", sentiment_counts.get("positive", 0))
c4.metric("Negative", sentiment_counts.get("negative", 0))

st.markdown("### Executive summary")
st.info(summary.get("summary", "No summary available."))

left, right = st.columns(2)
with left:
    st.markdown("### Positive themes")
    for theme in summary.get("positive_themes", []):
        st.success(theme)
with right:
    st.markdown("### Emerging risks")
    for risk in summary.get("emerging_risks", []):
        st.error(risk)

st.markdown("### Sentiment buckets")
buckets = report.get("sentiment_buckets", {})
tabs = st.tabs(["Positive", "Negative", "Neutral"])
for tab, key in zip(tabs, ["positive", "negative", "neutral"]):
    with tab:
        items = buckets.get(key, [])
        if not items:
            st.caption(f"No {key} examples.")
        for item in items[:10]:
            st.markdown(f"**{item.get('title', 'Untitled')}** {source_link(item.get('url', ''))}")
            st.caption(f"{item.get('source_type', 'web')} · {item.get('query_label', '')}")
            st.write(item.get("snippet") or item.get("content", ""))

st.markdown("### Source breakdown")
source_df = pd.DataFrame(report.get("source_breakdown", []))
if not source_df.empty:
    st.bar_chart(source_df.set_index("source_type"))
    st.dataframe(source_df, use_container_width=True)
else:
    st.caption("No source breakdown available.")

st.markdown("### Representative examples")
examples = pd.DataFrame(report.get("representative_examples", []))
if not examples.empty:
    cols = [c for c in ["sentiment", "source_type", "query_label", "title", "url", "snippet"] if c in examples.columns]
    st.dataframe(examples[cols], use_container_width=True, hide_index=True)
else:
    st.caption("No examples available.")

st.markdown("### Query summaries")
for query in report.get("query_summaries", []):
    with st.expander(f"{query.get('label')} · {query.get('focus')} · {query.get('result_count')} results"):
        st.code(query.get("query", ""))
        answer = query.get("answer")
        if answer:
            st.write(answer)

st.markdown("### Recommended follow-up searches")
for search in report.get("recommended_follow_up_searches", []):
    st.write(f"- {search}")

st.markdown("### Product / marketing actions")
for action in report.get("product_marketing_actions", []):
    st.write(f"- {action}")

with st.expander("Raw normalized results"):
    st.json(normalized[:50])
