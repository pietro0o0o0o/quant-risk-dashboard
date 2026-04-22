# 📊 Quantitative Risk Dashboard

> Real-time portfolio risk analytics built with Python, Streamlit, and Plotly.

**[🚀 Live Demo](https://your-app.streamlit.app)** — enter any ticker and explore risk metrics instantly.

---

## Features

- **Real-time data** via Yahoo Finance (yfinance)
- **Risk metrics**: VaR, CVaR, Sharpe, Sortino, Beta, Alpha, Max Drawdown
- **Visualizations**: cumulative returns vs benchmark, rolling drawdown, return distribution
- **Statistical tests**: Jarque-Bera normality test, skewness, excess kurtosis
- **Monte Carlo simulation**: GBM-based price path simulation with confidence bands
- **Rolling correlation** with configurable benchmark (SPY, QQQ, IWM, VTI)
- Fully interactive sidebar — change ticker, period, confidence level, RF rate on the fly

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data | `yfinance`, `pandas` |
| Quant | `numpy`, `scipy` |
| Viz | `plotly` |
| App | `streamlit` |
| Deploy | Streamlit Cloud |

## Run locally

```bash
git clone https://github.com/YOUR_USERNAME/quant-risk-dashboard
cd quant-risk-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Methodology

### Value at Risk (VaR)
Historical simulation VaR at configurable confidence level α:

$$\text{VaR}_\alpha = -Q_\alpha(r_t)$$

### Conditional VaR (Expected Shortfall)
$$\text{CVaR}_\alpha = -E[r_t \mid r_t \leq \text{VaR}_\alpha]$$

### Sharpe Ratio
$$\text{Sharpe} = \frac{R_p - R_f}{\sigma_p}$$

### Monte Carlo (GBM)
$$S_{t+\Delta t} = S_t \cdot \exp\left[\left(\mu - \frac{\sigma^2}{2}\right)\Delta t + \sigma\sqrt{\Delta t}\,Z\right], \quad Z \sim \mathcal{N}(0,1)$$

## Project Structure

```
quant-risk-dashboard/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md
```

## Author

Built as part of a quantitative finance portfolio.  
Connect on [LinkedIn](https://linkedin.com/in/YOUR_PROFILE).

---

*For educational purposes only. Not financial advice.*
