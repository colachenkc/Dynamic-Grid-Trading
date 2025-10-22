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

## ⚙️ Setup & Usage  

### 1. Installation  

```bash
git clone <your-repo-url>
cd <repo-name>
pip install -r requirements.txt
```

### 2. Prepare Data  
Fetch minute-level cryptocurrency data (e.g. from Binance API) and save it in the `data/` directory.

### 3. Configure Parameters  
Adjust the grid parameters, transaction fees, and other settings in `config.yaml`:

```yaml
symbol: BTCUSDT
grid_size: 0.02
grid_levels: 6
transaction_fee: 0.001
capital: 10000
```

### 4. Run Backtest  

```bash
python src/backtest.py --config config.yaml
```

### 5. Analyze Results  
Outputs include:
- **Equity curve**
- **Internal rate of return (IRR)**
- **Max drawdown**
- **Performance comparison** against buy-and-hold & static grid

---

## 🧠 Why It Matters  

- Provides a **theoretical correction** to misconceptions about “profitable” grid strategies.  
- Offers a **simple, robust, and adaptive** approach for volatile assets.  
- Serves as a **research foundation** for quantitative strategy development and market-adaptive algorithmic systems.  

---

## ⚠️ Disclaimer  

> Grid trading carries significant risk.  
> Back-test results are not indicative of future performance.  
> Use this codebase for **research and educational purposes only.**

---

## 🚀 Possible Extensions  

- Multi-asset portfolio back-testing  
- Volatility-adaptive grid spacing  
- Stop-loss / take-profit overlays  
- Integration with trend filters or ML-based volatility forecasting  
- Real-time trading via exchange APIs  

---

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

**Let’s build and explore the Dynamic Grid Trading Strategy together! 🧩**

*Last updated: October 2025*
