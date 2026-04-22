import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats

st.set_page_config(
    page_title="Quant Risk Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card { background: #0e1117; border-radius: 8px; padding: 1rem; border: 1px solid #1e2130; }
    .stMetric { background: #0e1117; border-radius: 8px; padding: 0.5rem; }
    h1 { font-size: 1.8rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Quantitative Risk Dashboard")
st.caption("Real-time portfolio risk analytics — built with Python & Streamlit")

with st.sidebar:
    st.header("Parameters")
    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    benchmark = st.selectbox("Benchmark", ["SPY", "QQQ", "IWM", "VTI"], index=0)
    period = st.selectbox("Period", ["6mo", "1y", "2y", "3y", "5y"], index=1)
    confidence = st.slider("VaR confidence level", 90, 99, 95)
    rf_rate = st.number_input("Risk-free rate (%)", value=4.0, step=0.1) / 100
    n_sim = st.slider("Monte Carlo simulations", 100, 2000, 500, step=100)
    horizon = st.slider("MC horizon (days)", 30, 252, 90)
    run = st.button("▶  Run analysis", use_container_width=True)

@st.cache_data(ttl=300)
def load_data(ticker, benchmark, period):
    t = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    b = yf.download(benchmark, period=period, auto_adjust=True, progress=False)
    if t.empty or b.empty:
        return None, None
    t = t["Close"].squeeze()
    b = b["Close"].squeeze()
    df = pd.DataFrame({"stock": t, "bench": b}).dropna()
    return df, yf.Ticker(ticker).info

def calc_metrics(df, confidence, rf_rate):
    rets = df["stock"].pct_change().dropna()
    bench_rets = df["bench"].pct_change().dropna()
    rets, bench_rets = rets.align(bench_rets, join="inner")

    ann_ret = rets.mean() * 252
    ann_vol = rets.std() * np.sqrt(252)
    sharpe = (ann_ret - rf_rate) / ann_vol

    alpha = 1 - confidence / 100
    var = np.percentile(rets, alpha * 100)
    cvar = rets[rets <= var].mean()

    cumulative = (1 + rets).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()

    tot_ret = (df["stock"].iloc[-1] - df["stock"].iloc[0]) / df["stock"].iloc[0]

    cov = np.cov(rets, bench_rets)
    beta = cov[0, 1] / cov[1, 1]
    alpha_val = ann_ret - rf_rate - beta * (bench_rets.mean() * 252 - rf_rate)

    sortino_denom = rets[rets < 0].std() * np.sqrt(252)
    sortino = (ann_ret - rf_rate) / sortino_denom if sortino_denom > 0 else np.nan

    skew = stats.skew(rets)
    kurt = stats.kurtosis(rets)

    return {
        "rets": rets, "bench_rets": bench_rets,
        "drawdown": drawdown, "cumulative": cumulative,
        "ann_ret": ann_ret, "ann_vol": ann_vol,
        "sharpe": sharpe, "sortino": sortino,
        "var": var, "cvar": cvar, "max_dd": max_dd,
        "tot_ret": tot_ret, "beta": beta, "alpha": alpha_val,
        "skew": skew, "kurt": kurt
    }

def monte_carlo(last_price, mu, sigma, n_sim, horizon):
    dt = 1
    paths = np.zeros((n_sim, horizon + 1))
    paths[:, 0] = last_price
    z = np.random.standard_normal((n_sim, horizon))
    for t in range(1, horizon + 1):
        paths[:, t] = paths[:, t-1] * np.exp(
            (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z[:, t-1]
        )
    return paths

if run or "metrics" not in st.session_state:
    with st.spinner(f"Loading {ticker} data…"):
        df, info = load_data(ticker, benchmark, period)

    if df is None:
        st.error(f"Could not load data for **{ticker}**. Check the ticker symbol.")
        st.stop()

    m = calc_metrics(df, confidence, rf_rate)
    st.session_state["metrics"] = m
    st.session_state["df"] = df
    st.session_state["info"] = info or {}
    st.session_state["ticker"] = ticker
    st.session_state["benchmark"] = benchmark

m = st.session_state["metrics"]
df = st.session_state["df"]
info = st.session_state["info"]
disp_ticker = st.session_state.get("ticker", ticker)
disp_bench = st.session_state.get("benchmark", benchmark)

company_name = info.get("longName", disp_ticker)
sector = info.get("sector", "")
st.subheader(f"{company_name} {'· ' + sector if sector else ''}")

cols = st.columns(6)
def fmt_pct(v): return f"{v*100:+.1f}%"
def fmt_2(v): return f"{v:.2f}"

cols[0].metric("Total return", fmt_pct(m["tot_ret"]))
cols[1].metric("Ann. volatility", f"{m['ann_vol']*100:.1f}%")
cols[2].metric("Sharpe ratio", fmt_2(m["sharpe"]))
cols[3].metric(f"VaR {confidence}% (1d)", fmt_pct(m["var"]))
cols[4].metric(f"CVaR {confidence}%", fmt_pct(m["cvar"]))
cols[5].metric("Max drawdown", fmt_pct(m["max_dd"]))

st.divider()

cols2 = st.columns(4)
cols2[0].metric("Sortino ratio", fmt_2(m["sortino"]) if not np.isnan(m["sortino"]) else "—")
cols2[1].metric("Beta", fmt_2(m["beta"]))
cols2[2].metric("Alpha (ann.)", fmt_pct(m["alpha"]))
cols2[3].metric("Kurtosis", fmt_2(m["kurt"]))

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Cumulative returns",
    "📉 Drawdown",
    "🔔 Return distribution",
    "🔗 Correlation",
    "🎲 Monte Carlo"
])

with tab1:
    stock_cum = ((1 + m["rets"]).cumprod() - 1) * 100
    bench_cum = ((1 + m["bench_rets"]).cumprod() - 1) * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_cum.index, y=stock_cum, name=disp_ticker,
                             line=dict(color="#4C9BE8", width=2)))
    fig.add_trace(go.Scatter(x=bench_cum.index, y=bench_cum, name=disp_bench,
                             line=dict(color="#888", width=1.5, dash="dash")))
    fig.update_layout(yaxis_title="Return (%)", height=380,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02),
                      margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=m["drawdown"].index, y=m["drawdown"]*100,
                              fill="tozeroy", fillcolor="rgba(226,75,74,0.2)",
                              line=dict(color="#E24B4A", width=1.5), name="Drawdown"))
    fig2.add_hline(y=m["max_dd"]*100, line=dict(color="#ff6b6b", dash="dot", width=1),
                   annotation_text=f"Max DD: {m['max_dd']*100:.1f}%")
    fig2.update_layout(yaxis_title="Drawdown (%)", height=350,
                       margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(x=m["rets"]*100, nbinsx=60,
                                marker_color="#534AB7", opacity=0.8, name="Daily returns"))
    fig3.add_vline(x=m["var"]*100, line=dict(color="#E24B4A", dash="dash", width=2),
                   annotation_text=f"VaR {confidence}%: {m['var']*100:.2f}%")
    fig3.add_vline(x=m["cvar"]*100, line=dict(color="#D85A30", dash="dot", width=2),
                   annotation_text=f"CVaR: {m['cvar']*100:.2f}%")
    fig3.update_layout(xaxis_title="Daily return (%)", yaxis_title="Frequency",
                       height=350, margin=dict(l=0,r=0,t=10,b=0))
    col_a, col_b = st.columns(2)
    col_a.plotly_chart(fig3, use_container_width=True)
    with col_b:
        st.markdown("**Distribution stats**")
        st.dataframe(pd.DataFrame({
            "Metric": ["Mean (daily)", "Std (daily)", "Skewness", "Excess kurtosis", "Min", "Max"],
            "Value": [
                f"{m['rets'].mean()*100:.3f}%",
                f"{m['rets'].std()*100:.3f}%",
                f"{m['skew']:.3f}",
                f"{m['kurt']:.3f}",
                f"{m['rets'].min()*100:.2f}%",
                f"{m['rets'].max()*100:.2f}%"
            ]
        }), hide_index=True, use_container_width=True)
        normality = stats.jarque_bera(m["rets"])
        st.caption(f"Jarque-Bera test: stat={normality.statistic:.1f}, p={normality.pvalue:.4f}")

with tab4:
    roll = m["rets"].rolling(30).corr(m["bench_rets"])
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=roll.index, y=roll,
                              line=dict(color="#1D9E75", width=2), name="30d rolling corr"))
    fig4.add_hline(y=m["rets"].corr(m["bench_rets"]),
                   line=dict(color="#888", dash="dash"),
                   annotation_text=f"Full period: {m['rets'].corr(m['bench_rets']):.2f}")
    fig4.update_layout(yaxis_title=f"Correlation with {disp_bench}",
                       yaxis_range=[-1,1], height=350, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig4, use_container_width=True)

with tab5:
    last_price = float(df["stock"].iloc[-1])
    mu_daily = float(m["rets"].mean())
    sigma_daily = float(m["rets"].std())
    paths = monte_carlo(last_price, mu_daily, sigma_daily, n_sim, horizon)
    finals = paths[:, -1]
    p5, p25, p50, p75, p95 = np.percentile(finals, [5, 25, 50, 75, 95])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Median exit", f"${p50:.2f}", f"{(p50-last_price)/last_price*100:+.1f}%")
    c2.metric("95th pct", f"${p95:.2f}", f"{(p95-last_price)/last_price*100:+.1f}%")
    c3.metric("5th pct", f"${p5:.2f}", f"{(p5-last_price)/last_price*100:+.1f}%")
    prob_up = np.mean(finals > last_price) * 100
    c4.metric("P(profit)", f"{prob_up:.1f}%")

    fig5 = go.Figure()
    step = max(1, n_sim // 100)
    for i in range(0, n_sim, step):
        fig5.add_trace(go.Scatter(y=paths[i], line=dict(color="rgba(55,138,221,0.08)", width=0.8),
                                  showlegend=False))
    fig5.add_trace(go.Scatter(y=np.percentile(paths, 95, axis=0),
                              line=dict(color="#1D9E75", width=2, dash="dash"), name="95th pct"))
    fig5.add_trace(go.Scatter(y=np.percentile(paths, 5, axis=0),
                              line=dict(color="#E24B4A", width=2, dash="dash"), name="5th pct"))
    fig5.add_trace(go.Scatter(y=np.median(paths, axis=0),
                              line=dict(color="#4C9BE8", width=2.5), name="Median"))
    fig5.add_hline(y=last_price, line=dict(color="#fff", dash="dot", width=1),
                   annotation_text="Current price")
    fig5.update_layout(yaxis_title="Price ($)", xaxis_title="Trading days",
                       height=400, margin=dict(l=0,r=0,t=10,b=0),
                       legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig5, use_container_width=True)

st.divider()
st.caption("⚠️ For educational purposes only. Not financial advice.")
