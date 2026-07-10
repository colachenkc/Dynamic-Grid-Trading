"""Order chart + performance metrics for one backtest config.

Usage: python orders.py <tag>_fills.csv <tag>_equity.csv [--start D] [--end D]
"""
import argparse
import pathlib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BLUE, RED, VIOLET = "#2a78d6", "#e34948", "#4a3aa7"
SURFACE, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("fills")
ap.add_argument("equity")
ap.add_argument("--principal", type=float, default=100.0, help="open-grid notional")
ap.add_argument("--start", help="YYYY-MM-DD")
ap.add_argument("--end", help="YYYY-MM-DD")
a = ap.parse_args()

fills_path, equity_path, principal = pathlib.Path(a.fills), pathlib.Path(a.equity), a.principal
fills = pd.read_csv(fills_path, parse_dates=["time"])
eq = pd.read_csv(equity_path, parse_dates=["time"]).sort_values("time").reset_index(drop=True)

if a.start or a.end:
    lo = pd.Timestamp(a.start) if a.start else eq["time"].min()
    hi = pd.Timestamp(a.end) if a.end else eq["time"].max()
    fills = fills[(fills["time"] >= lo) & (fills["time"] <= hi)]
    eq = eq[(eq["time"] >= lo) & (eq["time"] <= hi)].reset_index(drop=True)

# ponytail: USDT+COIN*price omits capital held inside the open grid, so the curve
# starts at 0. Approximate the open grid at its notional. Error <= one grid band.
eq["value_adj"] = eq["value"] + principal

# Time-weighted return: strip out capital injections so the return is the
# return *the capital earned*, not a reward for injecting more of it.
flow = eq["money_input"].diff().fillna(0.0)
prev = eq["value_adj"].shift(1)
eq["r"] = (eq["value_adj"] - flow - prev) / prev
eq.loc[0, "r"] = 0.0
eq["twr"] = (1 + eq["r"]).cumprod()
eq["hold"] = eq["close"] / eq["close"].iloc[0]

years = (eq["time"].iloc[-1] - eq["time"].iloc[0]).days / 365.25


def stats(index: pd.Series, daily: pd.Series) -> dict:
    total = index.iloc[-1]
    dd = (index / index.cummax() - 1).min()
    sharpe = daily.mean() / daily.std() * np.sqrt(365) if daily.std() > 0 else float("nan")
    return {
        "total return": f"{(total - 1) * 100:,.1f}%",
        "annualized": f"{(total ** (1 / years) - 1) * 100:,.1f}%",
        "max drawdown": f"{dd * 100:,.1f}%",
        "sharpe": f"{sharpe:.2f}",
    }


strat = stats(eq["twr"], eq["r"])
hold = stats(eq["hold"], eq["close"].pct_change().fillna(0.0))

n_buy = int((fills["side"] == "buy").sum())
n_sell = int((fills["side"] == "sell").sum())
peak_capital = eq["money_input"].max()
final_value = eq["value_adj"].iloc[-1]

print(f"\nperiod {eq['time'].iloc[0]:%Y-%m-%d} -> {eq['time'].iloc[-1]:%Y-%m-%d}  ({years:.2f}y)")
print(f"fills: {len(fills):,}  ({n_buy:,} buy / {n_sell:,} sell)")
print(f"capital injected: {peak_capital:,.0f}   final value: {final_value:,.0f}   simple multiple: {final_value/peak_capital:.2f}x")
print(f"\n{'metric':<16}{'DGT (time-wtd)':>18}{'buy & hold':>14}")
for k in strat:
    print(f"{k:<16}{strat[k]:>18}{hold[k]:>14}")
print()

fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
    row_heights=[0.46, 0.30, 0.24],
    subplot_titles=("Price and fills", "Growth of 1 (time-weighted)", "Capital injected"),
)

fig.add_trace(go.Scatter(x=eq["time"], y=eq["close"], name="BTC price",
                         line=dict(color=MUTED, width=1)), row=1, col=1)
# colour = direction (buy/sell), symbol = kind (rung crossing vs grid break)
SERIES = (("buy", BLUE, "triangle-up", 5), ("sell", RED, "triangle-down", 5),
          ("enter", BLUE, "x", 9), ("exit", RED, "x", 9))
for side, color, sym, size in SERIES:
    f = fills[fills["side"] == side]
    if f.empty:
        continue
    label = {"enter": "down-break: buy inventory", "exit": "up-break: sell inventory"}.get(side, f"{side} rung")
    fig.add_trace(go.Scatter(x=f["time"], y=f["price"], name=f"{label} ({len(f):,})",
                             mode="markers",
                             marker=dict(color=color, size=size, symbol=sym,
                                         line=dict(color=SURFACE, width=0.5)),
                             hovertemplate=f"{label} %{{y:,.0f}}<br>%{{x|%Y-%m-%d %H:%M}}<extra></extra>"),
                  row=1, col=1)

fig.add_trace(go.Scatter(x=eq["time"], y=eq["twr"], name="DGT", line=dict(color=BLUE, width=2)), row=2, col=1)
fig.add_trace(go.Scatter(x=eq["time"], y=eq["hold"], name="buy & hold", line=dict(color=VIOLET, width=2)), row=2, col=1)
fig.add_trace(go.Scatter(x=eq["time"], y=eq["money_input"], name="capital in",
                         fill="tozeroy", line=dict(color=VIOLET, width=1.5)), row=3, col=1)

sub = (f"DGT {strat['total return']} vs hold {hold['total return']}  ·  "
       f"maxDD {strat['max drawdown']} vs {hold['max drawdown']}  ·  "
       f"{peak_capital:,.0f} USDT injected across {len(fills):,} fills")
fig.update_layout(
    title=dict(text=f"{fills_path.stem.replace('_fills','')}<br><sub>{sub}</sub>"),
    template="plotly_white", plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
    font=dict(color=INK), hovermode="x unified", height=900,
    legend=dict(orientation="h", y=1.06, x=0),
)
fig.update_yaxes(title_text="USDT", row=1, col=1)
fig.update_yaxes(title_text="growth of 1", type="log", row=2, col=1)
fig.update_yaxes(title_text="USDT", row=3, col=1)

out = fills_path.with_name(fills_path.stem.replace("_fills", "") + "_orders.html")
fig.write_html(out)
print(f"wrote {out}")
