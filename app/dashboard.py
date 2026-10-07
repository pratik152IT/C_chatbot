import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Local LLM Comparison", layout="wide")

TASK_ORDER = ["write", "debug", "explain", "qa"]


@st.cache_data
def load():
  # Point to CSV in data folder
  return pd.read_csv("data/eval_c_results.csv")


df = load()

st.title("Local LLM comparison: C programming")
st.caption(
    "Ollama models tested on writing, debugging and explaining C code, and"
    " answering C questions."
)

# ---- sidebar filters
st.sidebar.header("Filters")
models = st.sidebar.multiselect(
    "Models", sorted(df.model.unique()), default=sorted(df.model.unique())
)
tasks = st.sidebar.multiselect("Tasks", TASK_ORDER, default=TASK_ORDER)
d = df[df.model.isin(models) & df.task.isin(tasks)]
if d.empty:
  st.warning("Select at least one model and one task.")
  st.stop()

# ---- summary per model
summary = (
    d.groupby("model")
    .agg(
        pass_rate=("passed", "mean"),
        latency=("latency_s", "mean"),
        tok_s=("tok_per_s", "mean"),
        flesch=("flesch", "mean"),
    )
    .reset_index()
)
summary["pass_rate"] *= 100

# ---- KPI cards
cols = st.columns(len(summary))
for col, (_, r) in zip(cols, summary.iterrows()):
  with col:
    st.subheader(r.model)
    st.metric("Pass rate", f"{r.pass_rate:.0f}%")
    st.metric("Avg latency", f"{r.latency:.1f} s")
    st.metric("Tokens/sec", f"{r.tok_s:.1f}")

st.divider()

# ---- charts by task
by_task = (
    d.groupby(["model", "task"])
    .agg(pass_rate=("passed", "mean"), latency=("latency_s", "mean"))
    .reset_index()
)
by_task["pass_rate"] *= 100

left, right = st.columns(2)
with left:
  fig = px.bar(
      by_task,
      x="task",
      y="pass_rate",
      color="model",
      barmode="group",
      category_orders={"task": TASK_ORDER},
      title="Pass rate by task (%)",
      labels={"pass_rate": "Pass rate (%)"},
  )
  st.plotly_chart(fig, use_container_width=True)
with right:
  fig = px.bar(
      by_task,
      x="task",
      y="latency",
      color="model",
      barmode="group",
      category_orders={"task": TASK_ORDER},
      title="Average latency by task (s)",
      labels={"latency": "Latency (s)"},
  )
  st.plotly_chart(fig, use_container_width=True)

# ---- accuracy vs speed trade-off
fig = px.scatter(
    summary,
    x="latency",
    y="pass_rate",
    color="model",
    text="model",
    title="Accuracy vs speed trade-off",
    labels={
        "latency": "Avg latency (s), lower is faster",
        "pass_rate": "Pass rate (%)",
    },
)
fig.update_traces(marker_size=16, textposition="top center")
st.plotly_chart(fig, use_container_width=True)

# ---- readability (prose tasks only)
prose = d[d.task.isin(["explain", "qa"])]
if not prose.empty:
  fl = prose.groupby("model").flesch.mean().reset_index()
  fig = px.bar(
      fl,
      x="model",
      y="flesch",
      color="model",
      title="Readability of explanations (Flesch, higher = easier)",
  )
  st.plotly_chart(fig, use_container_width=True)

# ---- failures for manual review
st.subheader("Failed tests (review these by hand)")
fails = d[d.passed == 0][["model", "task", "name", "latency_s", "response"]]
st.dataframe(fails, use_container_width=True) if not fails.empty else st.success(
    "No failures."
)

with st.expander("Raw data"):
  st.dataframe(d, use_container_width=True)