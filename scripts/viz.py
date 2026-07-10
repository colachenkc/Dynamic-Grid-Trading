"""Heatmap of the backtest parameter sweep. Usage: python viz.py <results.csv> [metric]"""
import re
import sys
import pathlib
import pandas as pd
import plotly.express as px

# loss -> neutral -> profit. Gray midpoint so zero reads as "nothing".
DIVERGING = [(0.0, "#e34948"), (0.5, "#f0efec"), (1.0, "#2a78d6")]

csv = pathlib.Path(sys.argv[1])
metric = sys.argv[2] if len(sys.argv) > 2 else "IRR"
name = csv.stem

df = pd.read_csv(csv)
df.columns = df.columns.str.replace(" ", "_")
if metric not in df:
    df[metric] = df.eval(metric)  # e.g. "total_value / input_money - 2.29"
pivot = df.pivot(index="grid_numbers_half", columns="grid_size", values=metric)

fig = px.imshow(
    pivot,
    text_auto=".1f",
    aspect="auto",
    origin="lower",
    color_continuous_scale=DIVERGING,
    color_continuous_midpoint=0,
    labels={"x": "grid size", "y": "half grid count", "color": f"{metric} %"},
    title=f"{name} — {metric} by grid parameters",
)
fig.update_traces(xgap=2, ygap=2, hovertemplate="grid size %{x}<br>half grids %{y}<br>" + metric + " %{z:.2f}%<extra></extra>")
fig.update_xaxes(type="category")
fig.update_yaxes(type="category")
fig.update_layout(template="plotly_white", plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb")

slug = re.sub(r"\W+", "_", metric).strip("_")
out = csv.with_name(f"{name}_{slug}.html")
fig.write_html(out)
print(f"wrote {out}")
