# Dynamic Grid Trading (DGT) Strategy  

This repository contains the implementation of the **Dynamic Grid-based Trading (DGT)** strategy proposed in the paper  
**“Dynamic Grid Trading Strategy: From Zero Expectation to Market Outperformance”**  
by *Kai-Yuan Chen, Kai-Hsin Chen & Jyh-Shing Roger Jang* ([arXiv:2506.11921](https://arxiv.org/abs/2506.11921)).  

It includes back-testing code, sample configuration files, and scripts that replicate and extend the experiments described in the paper.

---

## 📖 Overview  

Traditional grid trading strategies — placing buy/sell orders at fixed price intervals — are theoretically **zero-expectation systems** under simple market assumptions.  
The authors propose a **Dynamic Grid Trading (DGT)** approach that resets the grid boundaries dynamically when prices break through predefined thresholds.  

This dynamic mechanism adapts to price trends and volatility, leading to **significant outperformance** in back-testing versus static grid and buy-and-hold strategies.

---

## 🧮 Key Contributions from the Paper  

- Mathematical proof showing traditional grid trading yields zero expected profit under ideal conditions.  
- Introduction of a **dynamic reset mechanism** that maintains profitability across market regimes.  
- Comprehensive back-testing on **BTC** and **ETH** minute-level data (Jan 2021 – Jul 2024).  
- Comparison of IRR and maximum drawdown showing consistent outperformance of DGT.  
- Theoretical foundation for extending grid trading to dynamic, adaptive frameworks.

---

## 📂 Project Structure
```
project/
│
├── src/
│   ├── config.py             # Global parameters (data path, grid sizes, fee config)
│   ├── grid_logic.py         # Core functions (grid resets, profit calc, settlement)
│   └── dgt_backtest.py       # Main backtest runner
│
├── scripts/
│   ├── fetch_candlestick.py  # Download OHLCV from Binance into data/
│   ├── grid_trading.py       # Static-grid baseline (paper experiment 1)
│   ├── viz.py                # Heatmap of the parameter sweep
│   └── orders.py             # Order chart + performance metrics for one config
│
├── data/                     # All CSV/HTML, gitignored — created on first fetch
│
└── README.md
```

---

## ⚙️ Setup & Usage  

### 1. Installation  

```bash
git clone <your-repo-url>
cd <repo-name>
pip install -r requirements.txt
```

### 2. Usage
1) Fetch market data. Writes `data/BTCUSDT_spot_1m.csv` (~300 MB, takes a while):
```bash
python scripts/fetch_candlestick.py
```
2) Configure parameters  
Edit src/config.py:
```bash
symbol = "BTCUSDT_spot"
start_time = "2021-01-01 00:00:00"
end_time   = "2024-07-31 23:59:00"

grid_sizes = [0.005, 0.01, 0.015, 0.02]
grid_numbers_half_list = [2, 3, 5]

grid_principal = 100
fee_pct = 0.0008
```
3) Run the parameter sweep. From project root:
```bash
python -m src.dgt_backtest
```

### 3. Analysis

Heatmap the sweep by any metric (default `IRR`, or an expression over the columns):
```bash
python scripts/viz.py data/BTCUSDT_spot_grid_strategy_backtest_results.csv IRR
```

For a single config, set `trade_log = (grid_size, grid_numbers_half)` in `src/config.py`
and re-run the backtest — it dumps `<tag>_fills.csv` and `<tag>_equity.csv` into `data/`.
Chart them, with performance versus buy & hold:
```bash
python scripts/orders.py data/<tag>_fills.csv data/<tag>_equity.csv
```

All output lands next to its input, in `data/`.
## 🙌 Welcome to Contributions!  

We welcome contributions from developers, quants, and researchers who wish to improve this project.  

### How to Contribute  

1. **Fork** this repository  
2. Create a new branch  
   ```bash
   git checkout -b feature/your-feature-name
   ```  
3. Make your changes and add tests  
4. **Commit** with clear messages  
5. **Push** to your fork and open a **Pull Request**

### Contribution Ideas  

- Add new back-testing modules or asset data sources  
- Develop a parameter optimization dashboard or CLI interface  
- Create visualizations (heatmaps, equity curves, parameter sweeps)  
- Implement paper-trading / live-trading wrappers  
- Enhance documentation and tutorial notebooks  

### Code of Conduct  

Please follow the [Contributor Covenant](https://www.contributor-covenant.org/) to maintain a respectful and collaborative community.

---

## 🧾 Citation  

If you use this repository or the ideas from the paper in your research or publication, please cite:  

```bibtex
@article{chen2025dynamic,
  title={Dynamic Grid Trading Strategy: From Zero Expectation to Market Outperformance},
  author={Chen, Kai-Yuan and Chen, Kai-Hsin and Jang, Jyh-Shing Roger},
  journal={arXiv preprint arXiv:2506.11921},
  year={2025},
  url={https://arxiv.org/abs/2506.11921}
}
