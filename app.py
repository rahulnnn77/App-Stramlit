# pyrefly: ignore [missing-import]
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os

# ─────────────────────────────────────────────────────────────
# Ticker Lists Configuration Constants
# ─────────────────────────────────────────────────────────────
NIFTY50_TICKERS = (
    "RELIANCE.NS, TCS.NS, HDFCBANK.NS, ICICIBANK.NS, INFY.NS, HINDUNILVR.NS, ITC.NS, "
    "SBIN.NS, BHARTIARTL.NS, KOTAKBANK.NS, BAJFINANCE.NS, LTIM.NS, HCLTECH.NS, ASIANPAINT.NS, "
    "AXISBANK.NS, MARUTI.NS, TITAN.NS, WIPRO.NS, NESTLEIND.NS, ULTRACEMCO.NS, SUNPHARMA.NS, "
    "POWERGRID.NS, NTPC.NS, TECHM.NS, INDUSINDBK.NS, TATAMOTORS.NS, TATASTEEL.NS, "
    "BAJAJFINSV.NS, M&M.NS, JSWSTEEL.NS, HDFCLIFE.NS, SBILIFE.NS, BRITANNIA.NS, CIPLA.NS, "
    "DRREDDY.NS, EICHERMOT.NS, GRASIM.NS, ADANIPORTS.NS, BPCL.NS, COALINDIA.NS, "
    "DIVISLAB.NS, HEROMOTOCO.NS, APOLLOHOSP.NS, TRENT.NS, HINDALCO.NS, LT.NS, "
    "ADANIENT.NS, BEL.NS, ONGC.NS, SHREECEM.NS"
)
NIFTY500_TICKERS = (
    "RELIANCE.NS, TCS.NS, HDFCBANK.NS, ICICIBANK.NS, INFY.NS, HINDUNILVR.NS, ITC.NS, "
    "SBIN.NS, BHARTIARTL.NS, KOTAKBANK.NS, BAJFINANCE.NS, LTIM.NS, HCLTECH.NS, ASIANPAINT.NS, "
    "AXISBANK.NS, MARUTI.NS, TITAN.NS, WIPRO.NS, NESTLEIND.NS, ULTRACEMCO.NS, SUNPHARMA.NS, "
    "POWERGRID.NS, NTPC.NS, TECHM.NS, INDUSINDBK.NS, TATAMOTORS.NS, TATASTEEL.NS, "
    "BAJAJFINSV.NS, M&M.NS, JSWSTEEL.NS, HDFCLIFE.NS, SBILIFE.NS, BRITANNIA.NS, CIPLA.NS, "
    "DRREDDY.NS, EICHERMOT.NS, GRASIM.NS, ADANIPORTS.NS, BPCL.NS, COALINDIA.NS, "
    "DIVISLAB.NS, HEROMOTOCO.NS, APOLLOHOSP.NS, TRENT.NS, HINDALCO.NS, LT.NS, "
    "ADANIENT.NS, BEL.NS, ONGC.NS, SHREECEM.NS, "
    "BAJAJ-AUTO.NS, ZOMATO.NS, PIDILITIND.NS, HAVELLS.NS, MUTHOOTFIN.NS, BERGEPAINT.NS, "
    "GODREJCP.NS, DABUR.NS, MARICO.NS, COLPAL.NS, TATACONSUM.NS, SIEMENS.NS, ABB.NS, "
    "ADANIGREEN.NS, TATAPOWER.NS, GAIL.NS, IOC.NS, HINDPETRO.NS, OFSS.NS, NAUKRI.NS, "
    "DLF.NS, LODHA.NS, GODREJPROP.NS, OBEROIRLTY.NS, IRCTC.NS, CONCOR.NS, HAL.NS, "
    "BHEL.NS, VEDL.NS, SAIL.NS, NMDC.NS, NATIONALUM.NS, HINDZINC.NS, "
    "LUPIN.NS, TORNTPHARM.NS, AUROPHARMA.NS, ALKEM.NS, BIOCON.NS, FORTIS.NS, MAXHEALTH.NS, "
    "MPHASIS.NS, LTTS.NS, COFORGE.NS, PERSISTENT.NS, KPITTECH.NS, TATAELXSI.NS, "
    "BANDHANBNK.NS, IDFCFIRSTB.NS, FEDERALBNK.NS, PNB.NS, CANBK.NS"
)
SECTOR_PRESETS = {
    "Banking": "HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, KOTAKBANK.NS, AXISBANK.NS, INDUSINDBK.NS, BANDHANBNK.NS, FEDERALBNK.NS, IDFCFIRSTB.NS, PNB.NS, CANBK.NS, UNIONBANK.NS",
    "IT": "TCS.NS, INFY.NS, WIPRO.NS, HCLTECH.NS, TECHM.NS, LTIM.NS, PERSISTENT.NS, MPHASIS.NS, COFORGE.NS, LTTS.NS, KPITTECH.NS, TATAELXSI.NS, OFSS.NS",
    "Auto": "TATAMOTORS.NS, M&M.NS, MARUTI.NS, EICHERMOT.NS, BAJAJ-AUTO.NS, HEROMOTOCO.NS, TVSMOTORS.NS, ASHOKLEY.NS, MOTHERSON.NS, TIINDIA.NS",
    "Pharma": "SUNPHARMA.NS, DRREDDY.NS, CIPLA.NS, DIVISLAB.NS, APOLLOHOSP.NS, LUPIN.NS, TORNTPHARM.NS, AUROPHARMA.NS, ALKEM.NS, BIOCON.NS, GLENMARK.NS, IPCALAB.NS",
    "Energy": "RELIANCE.NS, ONGC.NS, BPCL.NS, HINDPETRO.NS, IOC.NS, GAIL.NS, ADANIGREEN.NS, TATAPOWER.NS, NTPC.NS, POWERGRID.NS, PETRONET.NS, IGL.NS",
    "FMCG": "HINDUNILVR.NS, ITC.NS, NESTLEIND.NS, BRITANNIA.NS, DABUR.NS, MARICO.NS, GODREJCP.NS, COLPAL.NS, TATACONSUM.NS, EMAMILTD.NS, JYOTHYLAB.NS",
    "Infra & Capital": "LT.NS, ADANIPORTS.NS, ADANIENT.NS, BEL.NS, HAL.NS, BHEL.NS, SIEMENS.NS, ABB.NS, CUMMINSIND.NS, TIINDIA.NS, GRSE.NS, MAZAGON.NS",
    "Metals": "TATASTEEL.NS, JSWSTEEL.NS, HINDALCO.NS, COALINDIA.NS, NMDC.NS, SAIL.NS, VEDL.NS, NATIONALUM.NS, HINDZINC.NS",
}

OPERATORS = [">", "<", ">=", "<=", "==", "!="]

# ─────────────────────────────────────────────────────────────
# Page Config (Sidebar is expanded by default for easy use)
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Alphaquanttester",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Handle strategy load-for-edit navigation redirection ──
if st.session_state.get("edit_load_requested"):
    st.session_state.sb_navigation = "Strategy"
    st.session_state.pop("edit_load_requested", None)

# ─────────────────────────────────────────────────────────────
# Sidebar Controls Hub (Rendered first to set Dark Theme state)
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">Alphaquanttester</div>', unsafe_allow_html=True)
    
    # ── Dark Mode Toggle ──
    dark_theme = st.toggle("Dark Theme 🌙", value=False, key="sb_dark_theme")

    st.markdown('<p class="section-label">Market Selection</p>', unsafe_allow_html=True)
    market_choice = st.segmented_control(
        "Market Option",
        options=["Indian market (NSE)", "US market"],
        default="Indian market (NSE)",
        key="sb_market",
        label_visibility="collapsed"
    )
    if not market_choice:
        market_choice = "Indian market (NSE)"

    st.markdown('<p class="section-label">Feature Navigation</p>', unsafe_allow_html=True)
    nav_choice = st.radio(
        "Feature Navigation Selection",
        options=["Data Downloader", "Screener", "Strategy", "Saved Strategies", "Charts", "Backtester"],
        key="sb_navigation",
        label_visibility="collapsed"
    )

# ─────────────────────────────────────────────────────────────
# Production CSS Style Customization (Plus Jakarta Sans)
# ─────────────────────────────────────────────────────────────
theme_css = ""
if dark_theme:
    # ── DARK THEME OVERRIDES ──
    theme_css = """
    /* Main Background & Text Color */
    html, body, [data-testid="stAppViewContainer"], .main, [data-testid="stHeader"] {
        background-color: #0C0C0E !important;
        color: #F2F2F7 !important;
    }
    
    /* Sidebar Overrides */
    [data-testid="stSidebar"], [data-testid="stSidebar"] [data-testid="element-container"] {
        background-color: #121214 !important;
        color: #F2F2F7 !important;
    }
    
    /* Cards (Container borders) */
    div[data-testid="element-container"] div[style*="border"] {
        background-color: #18181C !important;
        border-color: #2C2C2E !important;
    }
    
    /* Metrics Widget */
    div[data-testid="stMetric"] {
        background-color: #18181C !important;
        border: 1px solid #2C2C2E !important;
    }
    div[data-testid="stMetric"]:hover {
        background-color: #222226 !important;
        border-color: #3A3A3C !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #8E8E93 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }
    
    /* Titles */
    .main-title {
        color: #FFFFFF !important;
    }
    .sub-title {
        color: #8E8E93 !important;
    }
    
    /* Input Boxes Dark Styles */
    div[data-baseweb="input"], input, textarea, select {
        background-color: #18181C !important;
        color: #FFFFFF !important;
        border-color: #2C2C2E !important;
    }
    
    /* Segmented Control Buttons */
    [data-testid="stSegmentedControl"] button {
        background-color: #18181C !important;
        color: #8E8E93 !important;
        border: 1px solid #2C2C2E !important;
    }
    [data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background-color: #0066cc !important;
        color: #FFFFFF !important;
        border-color: #0066cc !important;
    }
    [data-testid="stSegmentedControl"] button:hover {
        background-color: #222226 !important;
        color: #FFFFFF !important;
    }
    
    /* Radio options highlight */
    div[role="radiogroup"] label {
        color: #8E8E93 !important;
        transition: color 0.15s ease;
    }
    div[role="radiogroup"] label[aria-checked="true"] {
        color: #0066cc !important;
        font-weight: 700 !important;
    }
    
    /* Primary buttons (Run Scan, save, run strategy) */
    button[kind="primary"], button[data-testid="baseButton-primary"] {
        background-color: #0066cc !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
        background-color: #0077ee !important;
    }
    
    /* Secondary buttons (Presets, sectors, clear, download) */
    button[kind="secondary"], button[data-testid="baseButton-secondary"], button {
        background-color: #18181C !important;
        color: #F2F2F7 !important;
        border: 1px solid #2C2C2E !important;
    }
    button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover, button:hover {
        background-color: #222226 !important;
        color: #FFFFFF !important;
        border-color: #3A3A3C !important;
    }
    
    /* Table backgrounds */
    div[data-testid="stDataFrame"] {
        background-color: #18181C !important;
    }
    """
else:
    # ── LIGHT THEME STYLE ──
    theme_css = """
    html, body, [data-testid="stAppViewContainer"], .main, [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
    }
    [data-testid="stSidebar"], [data-testid="stSidebar"] [data-testid="element-container"] {
        background-color: #F5F5F7 !important;
        color: #1D1D1F !important;
    }
    div[data-testid="element-container"] div[style*="border"] {
        background-color: #FFFFFF !important;
        border-color: #D2D2D7 !important;
    }
    div[data-testid="stMetric"] {
        background-color: #F5F5F7 !important;
        border: 1px solid #D2D2D7 !important;
    }
    div[data-testid="stMetric"]:hover {
        background-color: #E8E8ED; border-color: #AEAEB2;
    }
    div[data-testid="stMetricLabel"] {
        color: #86868B !important;
    }
    div[data-testid="stMetricValue"] {
        color: #1D1D1F !important;
    }
    .main-title {
        color: #1D1D1F !important;
    }
    .sub-title {
        color: #86868B !important;
    }
    
    /* Segmented Control Buttons */
    [data-testid="stSegmentedControl"] button {
        background-color: #F5F5F7 !important;
        color: #86868B !important;
        border: 1px solid #D2D2D7 !important;
    }
    [data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background-color: #0066cc !important;
        color: #FFFFFF !important;
        border-color: #0066cc !important;
    }
    [data-testid="stSegmentedControl"] button:hover {
        background-color: #E8E8ED !important;
        color: #1D1D1F !important;
    }
    
    /* Radio options highlight */
    div[role="radiogroup"] label {
        color: #86868B !important;
        transition: color 0.15s ease;
    }
    div[role="radiogroup"] label[aria-checked="true"] {
        color: #0066cc !important;
        font-weight: 700 !important;
    }
    
    /* Primary buttons */
    button[kind="primary"], button[data-testid="baseButton-primary"] {
        background-color: #0066cc !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
        background-color: #0077ee !important;
    }
    
    /* Secondary buttons */
    button[kind="secondary"], button[data-testid="baseButton-secondary"], button {
        background-color: #F5F5F7 !important;
        color: #1D1D1F !important;
        border: 1px solid #D2D2D7 !important;
    }
    button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover, button:hover {
        background-color: #E8E8ED !important;
        border-color: #AEAEB2 !important;
        color: #1D1D1F !important;
    }
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Global Font Override - targets text elements and preserves icon fonts naturally */
html, body, p, label, button, input, select, textarea, h1, h2, h3, h4, h5, h6 {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}}

.stMarkdown, .stButton, .stWidget, div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"], .section-label, .main-title, .sub-title, .sidebar-title, .stRadio, .stSelectbox {{
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}}

.main-title {{
    font-size: 2.8rem; font-weight: 800;
    margin-top: 0.5rem; margin-bottom: 0.1rem;
    letter-spacing: -0.04em;
}}
.sub-title {{
    font-size: 1.05rem; font-weight: 400;
    margin-bottom: 1.5rem;
}}
div[data-testid="stMetricValue"] {{
    letter-spacing: -0.02em;
}}
.section-label {{
    font-size: 0.72rem; font-weight: 800; color: #86868B;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; margin-top: 15px;
}}
.sidebar-title {{
    font-size: 1.45rem; font-weight: 800;
    margin-bottom: 20px; letter-spacing: -0.03em;
}}
.saved-strategy-card {{
    background-color: #F5F5F7; border: 1px solid #D2D2D7;
    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
}}

{theme_css}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Technical Indicator Functions
# ─────────────────────────────────────────────────────────────
def compute_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def compute_sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    return 100 - (100 / (1 + rs))

def compute_adx_full(df: pd.DataFrame, period: int = 14):
    high, low, close = df['High'], df['Low'], df['Close']
    prev_high, prev_low, prev_close = high.shift(1), low.shift(1), close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    up_move, down_move = high - prev_high, prev_low - low
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False).mean() / (atr + 1e-9)
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False).mean() / (atr + 1e-9)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-9)
    adx = dx.ewm(alpha=1 / period, adjust=False).mean()
    return adx, plus_di, minus_di

def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def compute_bollinger(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    mid = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = mid + std_dev * std
    lower = mid - std_dev * std
    return upper, mid, lower

def compute_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3):
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    k = 100 * (df['Close'] - low_min) / (high_max - low_min + 1e-9)
    d = k.rolling(window=d_period).mean()
    return k, d

def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df['High'], df['Low'], df['Close']
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()

def compute_cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
    typical = (df['High'] + df['Low'] + df['Close']) / 3
    sma = typical.rolling(window=period).mean()
    mad = typical.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
    return (typical - sma) / (0.015 * mad + 1e-9)

def compute_williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_max = df['High'].rolling(window=period).max()
    low_min = df['Low'].rolling(window=period).min()
    return -100 * (high_max - df['Close']) / (high_max - low_min + 1e-9)

def compute_vwap(df: pd.DataFrame) -> pd.Series:
    typical = (df['High'] + df['Low'] + df['Close']) / 3
    return (typical * df['Volume']).cumsum() / (df['Volume'].cumsum() + 1e-9)

def compute_obv(df: pd.DataFrame) -> pd.Series:
    direction = df['Close'].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    return (direction * df['Volume']).cumsum()

def compute_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    typical = (df['High'] + df['Low'] + df['Close']) / 3
    raw_mf = typical * df['Volume']
    pos_mf = raw_mf.where(typical > typical.shift(1), 0.0)
    neg_mf = raw_mf.where(typical < typical.shift(1), 0.0)
    mf_ratio = pos_mf.rolling(window=period).sum() / (neg_mf.rolling(window=period).sum() + 1e-9)
    return 100 - (100 / (1 + mf_ratio))

def compute_roc(series: pd.Series, period: int = 10) -> pd.Series:
    return 100 * (series - series.shift(period)) / (series.shift(period) + 1e-9)

# ─────────────────────────────────────────────────────────────
# Vectorized Indicators History Calculation Helper
# ─────────────────────────────────────────────────────────────
def compute_indicators_history(tdf: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    df = tdf.copy()
    if len(df) < 14:
        return df

    close = df['Close']
    
    # Always-computed rolling statistics
    df["52W High"] = close.rolling(window=252, min_periods=1).max()
    df["52W Low"]  = close.rolling(window=252, min_periods=1).min()
    df["% from 52W High"] = ((close - df["52W High"]) / (df["52W High"] + 1e-9)) * 100
    df["% from 52W Low"]  = ((close - df["52W Low"])  / (df["52W Low"]  + 1e-9)) * 100

    vol_series = df['Volume']
    df["Vol 20D Avg"] = vol_series.rolling(window=20, min_periods=1).mean().shift(1)
    df["Vol vs 20D Avg %"] = ((df["Volume"] - df["Vol 20D Avg"]) / (df["Vol 20D Avg"] + 1e-9)) * 100

    if cfg.get("enable_ema"):
        for p in cfg.get("ema_periods", []):
            if len(close) >= p:
                df[f"EMA {p}"] = compute_ema(close, p)

    if cfg.get("enable_sma"):
        for p in cfg.get("sma_periods", []):
            if len(close) >= p:
                df[f"SMA {p}"] = compute_sma(close, p)

    if cfg.get("enable_rsi"):
        df[f"RSI {cfg.get('rsi_period', 14)}"] = compute_rsi(close, cfg.get("rsi_period", 14))

    if cfg.get("enable_adx"):
        p = cfg.get("adx_period", 14)
        adx, plus_di, minus_di = compute_adx_full(df, p)
        df[f"ADX {p}"] = adx
        df[f"+DI {p}"] = plus_di
        df[f"-DI {p}"] = minus_di

    if cfg.get("enable_macd"):
        f, s, sig = cfg.get("macd_fast", 12), cfg.get("macd_slow", 26), cfg.get("macd_signal", 9)
        ml, sl, hist = compute_macd(close, f, s, sig)
        df[f"MACD ({f},{s})"] = ml
        df[f"Signal ({sig})"] = sl
        df["MACD Hist"] = hist

    if cfg.get("enable_bb"):
        p = cfg.get("bb_period", 20)
        upper, mid, lower = compute_bollinger(close, p)
        df[f"BB Upper ({p})"] = upper
        df[f"BB Mid ({p})"]   = mid
        df[f"BB Lower ({p})"] = lower
        df["BB %B"]           = (close - lower) / (upper - lower + 1e-9)

    if cfg.get("enable_stoch"):
        k, d = compute_stochastic(df, cfg.get("stoch_k", 14), cfg.get("stoch_d", 3))
        df[f"Stoch %K ({cfg.get('stoch_k', 14)})"] = k
        df[f"Stoch %D ({cfg.get('stoch_d', 3)})"] = d

    if cfg.get("enable_atr"):
        df[f"ATR {cfg.get('atr_period', 14)}"] = compute_atr(df, cfg.get("atr_period", 14))

    if cfg.get("enable_cci"):
        df[f"CCI {cfg.get('cci_period', 20)}"] = compute_cci(df, cfg.get("cci_period", 20))

    if cfg.get("enable_willr"):
        df[f"Williams %R ({cfg.get('willr_period', 14)})"] = compute_williams_r(df, cfg.get('willr_period', 14))

    if cfg.get("enable_vwap"):
        df["VWAP"] = compute_vwap(df)

    if cfg.get("enable_obv"):
        df["OBV"] = compute_obv(df)

    if cfg.get("enable_mfi"):
        df[f"MFI {cfg.get('mfi_period', 14)}"] = compute_mfi(df, cfg.get("mfi_period", 14))

    if cfg.get("enable_roc"):
        df[f"ROC {cfg.get('roc_period', 10)}"] = compute_roc(close, cfg.get("roc_period", 10))

    return df

# ─────────────────────────────────────────────────────────────
# Strategy Mask Filtering Helper
# ─────────────────────────────────────────────────────────────
def apply_strategy(df: pd.DataFrame, conditions: list[dict], match_mode: str) -> pd.DataFrame:
    if df.empty or not conditions:
        return df

    masks = []
    for cond in conditions:
        lhs_col = cond.get("lhs_col", "")
        op      = cond.get("op", ">")
        rhs_type = cond.get("rhs_type", "Value")
        rhs_val  = cond.get("rhs_val", 0.0)
        rhs_col  = cond.get("rhs_col", "")

        if lhs_col not in df.columns:
            continue

        lhs = df[lhs_col].astype(float)
        if rhs_type == "Value":
            rhs = float(rhs_val)
        elif rhs_type == "Column" and rhs_col in df.columns:
            rhs = df[rhs_col].astype(float)
        else:
            continue

        if op == ">":   masks.append(lhs > rhs)
        elif op == "<": masks.append(lhs < rhs)
        elif op == ">=": masks.append(lhs >= rhs)
        elif op == "<=": masks.append(lhs <= rhs)
        elif op == "==": masks.append(lhs == rhs)
        elif op == "!=": masks.append(lhs != rhs)

    if not masks:
        return df

    combined = masks[0]
    for m in masks[1:]:
        combined = combined & m if "AND" in match_mode else combined | m

    return df[combined]

# ─────────────────────────────────────────────────────────────
# Vectorized Strategy Trigger evaluator helper
# ─────────────────────────────────────────────────────────────
def apply_strategy_history(df: pd.DataFrame, conditions: list[dict], match_mode: str) -> pd.Series:
    if df.empty or not conditions:
        return pd.Series(False, index=df.index)

    masks = []
    for cond in conditions:
        lhs_col = cond.get("lhs_col", "")
        op      = cond.get("op", ">")
        rhs_type = cond.get("rhs_type", "Value")
        rhs_val  = cond.get("rhs_val", 0.0)
        rhs_col  = cond.get("rhs_col", "")

        if lhs_col not in df.columns:
            continue

        lhs = df[lhs_col].astype(float)
        if rhs_type == "Value":
            rhs = float(rhs_val)
        elif rhs_type == "Column" and rhs_col in df.columns:
            rhs = df[rhs_col].astype(float)
        else:
            continue

        if op == ">":   masks.append(lhs > rhs)
        elif op == "<": masks.append(lhs < rhs)
        elif op == ">=": masks.append(lhs >= rhs)
        elif op == "<=": masks.append(lhs <= rhs)
        elif op == "==": masks.append(lhs == rhs)
        elif op == "!=": masks.append(lhs != rhs)

    if not masks:
        return pd.Series(False, index=df.index)

    combined = masks[0]
    for m in masks[1:]:
        combined = combined & m if "AND" in match_mode else combined | m

    return combined

# ─────────────────────────────────────────────────────────────
# Persistence Logic for Custom Strategies
# ─────────────────────────────────────────────────────────────
STRATEGY_FILE = "saved_strategies.json"

def load_saved_strategies() -> dict:
    if os.path.exists(STRATEGY_FILE):
        try:
            with open(STRATEGY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_custom_strategy(name: str, entry_conds: list, exit_conds: list, stop_loss_pct: float, entry_mode: str, exit_mode: str, cfg: dict) -> bool:
    all_strats = load_saved_strategies()
    all_strats[name] = {
        "entry_conditions": entry_conds,
        "exit_conditions": exit_conds,
        "stop_loss_pct": float(stop_loss_pct),
        "entry_match_mode": entry_mode,
        "exit_match_mode": exit_mode,
        "cfg": cfg,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open(STRATEGY_FILE, "w") as f:
            json.dump(all_strats, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Failed to persist strategy configuration: {e}")
        return False

def delete_custom_strategy(name: str) -> bool:
    all_strats = load_saved_strategies()
    if name in all_strats:
        del all_strats[name]
        try:
            with open(STRATEGY_FILE, "w") as f:
                json.dump(all_strats, f, indent=4)
            return True
        except Exception as e:
            st.error(f"Failed to delete strategy: {e}")
            return False
    return False

# ─────────────────────────────────────────────────────────────
# Data Loading & Utility Helpers
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_stock_data(ticker, start_date, end_date, interval_str):
    interval_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
    try:
        df = yf.download(ticker, start=start_date.strftime("%Y-%m-%d"),
                         end=end_date.strftime("%Y-%m-%d"),
                         interval=interval_map.get(interval_str, "1d"))
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}", icon=":material/error:")
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def load_screener_data(tickers_tuple, interval_str="Daily"):
    interval_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
    yfinance_interval = interval_map.get(interval_str, "1d")
    try:
        df = yf.download(list(tickers_tuple), period="2y", interval=yfinance_interval)
        return df
    except Exception:
        return pd.DataFrame()

def format_volume(v):
    if v >= 1e9: return f"{v/1e9:.2f}B"
    if v >= 1e6: return f"{v/1e6:.2f}M"
    if v >= 1e3: return f"{v/1e3:.2f}K"
    return str(int(v))

def parse_periods(text: str, default: list) -> list:
    try:
        p = [int(x.strip()) for x in text.split(",") if x.strip().isdigit() and int(x.strip()) > 0]
        return p if p else default
    except Exception:
        return default

# ─────────────────────────────────────────────────────────────
# Ticker Screen Computation Logic
# ─────────────────────────────────────────────────────────────
def screen_ticker(tdf: pd.DataFrame, cfg: dict) -> dict | None:
    if len(tdf) < 14:
        return None
    close = tdf['Close']
    latest, prev = tdf.iloc[-1], (tdf.iloc[-2] if len(tdf) > 1 else None)
    close_val = float(latest['Close'])
    vol_val   = float(latest['Volume'])
    pct = ((close_val - float(prev['Close'])) / (abs(float(prev['Close'])) + 1e-9) * 100) if prev is not None else 0.0

    # ── Always-computed market data ──────────────────────────
    lookback_252 = close.iloc[-252:] if len(close) >= 252 else close
    week52_high = float(lookback_252.max())
    week52_low  = float(lookback_252.min())
    pct_from_52h = ((close_val - week52_high) / (week52_high + 1e-9)) * 100
    pct_from_52l = ((close_val - week52_low)  / (week52_low  + 1e-9)) * 100

    vol_series   = tdf['Volume']
    vol_avg_20   = float(vol_series.iloc[-21:-1].mean()) if len(vol_series) > 21 else float(vol_series.mean())
    vol_chg_pct  = ((vol_val - vol_avg_20) / (vol_avg_20 + 1e-9)) * 100

    row = {
        "Close": close_val,
        "Change %": pct,
        "52W High": week52_high,
        "52W Low": week52_low,
        "% from 52W High": round(pct_from_52h, 2),
        "% from 52W Low":  round(pct_from_52l, 2),
        "Vol vs 20D Avg %": round(vol_chg_pct, 2),
    }

    if cfg.get("enable_ema"):
        for p in cfg.get("ema_periods", []):
            if len(close) >= p:
                row[f"EMA {p}"] = float(compute_ema(close, p).iloc[-1])

    if cfg.get("enable_sma"):
        for p in cfg.get("sma_periods", []):
            if len(close) >= p:
                row[f"SMA {p}"] = float(compute_sma(close, p).iloc[-1])

    if cfg.get("enable_rsi"):
        rsi_s = compute_rsi(close, cfg.get("rsi_period", 14))
        row[f"RSI {cfg.get('rsi_period', 14)}"] = float(rsi_s.iloc[-1]) if not rsi_s.empty else None

    if cfg.get("enable_adx"):
        adx_s, pdi_s, mdi_s = compute_adx_full(tdf, cfg.get("adx_period", 14))
        row[f"ADX {cfg.get('adx_period', 14)}"]  = float(adx_s.iloc[-1])
        row[f"+DI {cfg.get('adx_period', 14)}"]  = float(pdi_s.iloc[-1])
        row[f"-DI {cfg.get('adx_period', 14)}"]  = float(mdi_s.iloc[-1])

    if cfg.get("enable_macd"):
        f, s, sig = cfg.get("macd_fast", 12), cfg.get("macd_slow", 26), cfg.get("macd_signal", 9)
        ml, sl, hist = compute_macd(close, f, s, sig)
        row[f"MACD ({f},{s})"]   = float(ml.iloc[-1])
        row[f"Signal ({sig})"]   = float(sl.iloc[-1])
        row["MACD Hist"]         = float(hist.iloc[-1])

    if cfg.get("enable_bb"):
        p = cfg.get("bb_period", 20)
        upper, mid, lower = compute_bollinger(close, p)
        u, l = float(upper.iloc[-1]), float(lower.iloc[-1])
        row[f"BB Upper ({p})"] = u
        row[f"BB Mid ({p})"]   = float(mid.iloc[-1])
        row[f"BB Lower ({p})"] = l
        row["BB %B"]           = (close_val - l) / (u - l + 1e-9)

    if cfg.get("enable_stoch"):
        k, d = compute_stochastic(tdf, cfg.get("stoch_k", 14), cfg.get("stoch_d", 3))
        row[f"Stoch %K ({cfg.get('stoch_k', 14)})"] = float(k.iloc[-1])
        row[f"Stoch %D ({cfg.get('stoch_d', 3)})"] = float(d.iloc[-1])

    if cfg.get("enable_atr"):
        row[f"ATR {cfg.get('atr_period', 14)}"] = float(compute_atr(tdf, cfg.get("atr_period", 14)).iloc[-1])

    if cfg.get("enable_cci"):
        row[f"CCI {cfg.get('cci_period', 20)}"] = float(compute_cci(tdf, cfg.get("cci_period", 20)).iloc[-1])

    if cfg.get("enable_willr"):
        row[f"Williams %R ({cfg.get('willr_period', 14)})"] = float(compute_williams_r(tdf, cfg.get("willr_period", 14)).iloc[-1])

    if cfg.get("enable_vwap"):
        row["VWAP"] = float(compute_vwap(tdf).iloc[-1])

    if cfg.get("enable_obv"):
        row["OBV"] = float(compute_obv(tdf).iloc[-1])

    if cfg.get("enable_mfi"):
        row[f"MFI {cfg.get('mfi_period', 14)}"] = float(compute_mfi(tdf, cfg.get("mfi_period", 14)).iloc[-1])

    if cfg.get("enable_roc"):
        row[f"ROC {cfg.get('roc_period', 10)}"] = float(compute_roc(close, cfg.get("roc_period", 10)).iloc[-1])

    row["Volume"] = vol_val
    return row

# ─────────────────────────────────────────────────────────────
# Backtesting Chronological Trades Simulator logic
# ─────────────────────────────────────────────────────────────
def run_backtest_simulation(ticker: str, df: pd.DataFrame, entry_conds: list, exit_conds: list, stop_loss_pct: float, entry_mode: str, exit_mode: str) -> list[dict]:
    if len(df) < 14:
        return []

    # Evaluate signal triggers chronologically
    entry_mask = apply_strategy_history(df, entry_conds, entry_mode)
    exit_mask  = apply_strategy_history(df, exit_conds, exit_mode)

    trades = []
    position = False
    entry_price = 0.0
    entry_date = None
    max_high = 0.0
    min_low = 999999.0

    for i in range(14, len(df)):
        current_price = float(df['Close'].iloc[i])
        current_high  = float(df['High'].iloc[i])
        current_low   = float(df['Low'].iloc[i])
        current_date  = df.index[i]

        if not position:
            # Check entry condition
            if entry_mask.iloc[i]:
                position = True
                entry_price = current_price
                entry_date = current_date
                max_high = current_high
                min_low = current_low
        else:
            # Maintain active trade metrics
            max_high = max(max_high, current_high)
            min_low  = min(min_low, current_low)

            # Check stop loss hit
            if stop_loss_pct > 0.0 and current_low <= entry_price * (1.0 - stop_loss_pct / 100.0):
                exit_price = entry_price * (1.0 - stop_loss_pct / 100.0)
                max_drawdown = -stop_loss_pct
                runup = ((max_high - entry_price) / entry_price) * 100
                trades.append({
                    "Ticker": ticker,
                    "Signal Date": entry_date.strftime("%Y-%m-%d") if hasattr(entry_date, 'strftime') else str(entry_date),
                    "Entry Price": round(entry_price, 2),
                    "Exit Date": current_date.strftime("%Y-%m-%d") if hasattr(current_date, 'strftime') else str(current_date),
                    "Exit Price": round(exit_price, 2),
                    "Max Run-up %": round(runup, 2),
                    "Max Drawdown %": round(max_drawdown, 2),
                    "Return %": round(-stop_loss_pct, 2),
                    "Exit Reason": "Stop Loss 🛑"
                })
                position = False

            # Check Exit condition
            elif exit_mask.iloc[i]:
                runup = ((max_high - entry_price) / entry_price) * 100
                drawdown = ((min_low - entry_price) / entry_price) * 100
                trade_ret = ((current_price - entry_price) / entry_price) * 100
                trades.append({
                    "Ticker": ticker,
                    "Signal Date": entry_date.strftime("%Y-%m-%d") if hasattr(entry_date, 'strftime') else str(entry_date),
                    "Entry Price": round(entry_price, 2),
                    "Exit Date": current_date.strftime("%Y-%m-%d") if hasattr(current_date, 'strftime') else str(current_date),
                    "Exit Price": round(current_price, 2),
                    "Max Run-up %": round(runup, 2),
                    "Max Drawdown %": round(drawdown, 2),
                    "Return %": round(trade_ret, 2),
                    "Exit Reason": "Exit Signal 🎯"
                })
                position = False

            # Close at last candle if still open
            elif i == len(df) - 1:
                runup = ((max_high - entry_price) / entry_price) * 100
                drawdown = ((min_low - entry_price) / entry_price) * 100
                trade_ret = ((current_price - entry_price) / entry_price) * 100
                trades.append({
                    "Ticker": ticker,
                    "Signal Date": entry_date.strftime("%Y-%m-%d") if hasattr(entry_date, 'strftime') else str(entry_date),
                    "Entry Price": round(entry_price, 2),
                    "Exit Date": current_date.strftime("%Y-%m-%d") if hasattr(current_date, 'strftime') else str(current_date),
                    "Exit Price": round(current_price, 2),
                    "Max Run-up %": round(runup, 2),
                    "Max Drawdown %": round(drawdown, 2),
                    "Return %": round(trade_ret, 2),
                    "Exit Reason": "End of History ⌛"
                })
                position = False

    return trades

# ─────────────────────────────────────────────────────────────
# Advanced Performance and Drawdowns Calculator
# ─────────────────────────────────────────────────────────────
def compute_backtest_drawdowns(trades_df, total_period_years=2.0) -> dict:
    if trades_df.empty:
        return {
            "max_dd_pct": 0.0,
            "max_dd_period": 0,
            "current_dd_pct": 0.0,
            "current_dd_period": 0,
            "num_drawdowns": 0,
            "mean_dd_pct": 0.0,
            "median_dd_pct": 0.0,
            "cagr_pct": 0.0,
            "calmar": 0.0
        }
        
    df_sorted = trades_df.sort_values(by="Exit Date").reset_index(drop=True)
    
    equity = [100.0]
    for r in df_sorted["Return %"]:
        next_eq = equity[-1] * (1.0 + r / 100.0)
        equity.append(next_eq)
        
    eq_series = pd.Series(equity)
    peaks = eq_series.cummax()
    drawdowns = ((eq_series - peaks) / (peaks + 1e-9)) * 100
    
    max_dd = float(drawdowns.min())
    current_dd = float(drawdowns.iloc[-1])
    
    in_dd = drawdowns < -1e-4
    
    dd_periods = []
    current_dd_period = 0
    max_dd_period = 0
    num_drawdowns = 0
    
    curr_len = 0
    for val in in_dd:
        if val:
            curr_len += 1
        else:
            if curr_len > 0:
                dd_periods.append(curr_len)
                num_drawdowns += 1
                if curr_len > max_dd_period:
                    max_dd_period = curr_len
            curr_len = 0
            
    if curr_len > 0:
        dd_periods.append(curr_len)
        num_drawdowns += 1
        current_dd_period = curr_len
        if curr_len > max_dd_period:
            max_dd_period = curr_len

    non_zero_dds = drawdowns[drawdowns < -1e-4]
    mean_dd = float(non_zero_dds.mean()) if not non_zero_dds.empty else 0.0
    median_dd = float(non_zero_dds.median()) if not non_zero_dds.empty else 0.0

    final_equity = eq_series.iloc[-1]
    initial_equity = eq_series.iloc[0]
    
    try:
        start_dt = pd.to_datetime(df_sorted["Signal Date"].min())
        end_dt = pd.to_datetime(df_sorted["Exit Date"].max())
        diff_years = (end_dt - start_dt).days / 365.25
        if diff_years < 0.1:
            diff_years = total_period_years
    except Exception:
        diff_years = total_period_years

    if diff_years > 0:
        cagr = ((final_equity / initial_equity) ** (1.0 / diff_years) - 1.0) * 100.0
    else:
        cagr = 0.0
        
    abs_max_dd = abs(max_dd)
    calmar = cagr / abs_max_dd if abs_max_dd > 0 else 0.0
    
    return {
        "max_dd_pct": max_dd,
        "max_dd_period": max_dd_period,
        "current_dd_pct": current_dd,
        "current_dd_period": current_dd_period,
        "num_drawdowns": num_drawdowns,
        "mean_dd_pct": mean_dd,
        "median_dd_pct": median_dd,
        "cagr_pct": cagr,
        "calmar": calmar
    }

# ─────────────────────────────────────────────────────────────
# Views Configuration & UI Controllers
# ─────────────────────────────────────────────────────────────

# --- DATA DOWNLOADER & CHARTS (SINGLE TICKER) ---
if nav_choice in ["Data Downloader", "Charts"]:
    st.markdown(f'<div class="main-title">{nav_choice}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Explore individual stock details and analytics.</div>', unsafe_allow_html=True)

    with st.container(border=True):
        col_t, col_i, col_d1, col_d2 = st.columns([2.5, 3.5, 2, 2])
        with col_t:
            ticker_input = st.text_input("Search ticker", value="AAPL", placeholder="e.g. AAPL, RELIANCE, TCS").strip().upper()
        with col_i:
            interval_choice = st.segmented_control("Interval", options=["Daily", "Weekly", "Monthly"], default="Daily")
            if not interval_choice: interval_choice = "Daily"
        with col_d1:
            default_start = datetime.today() - timedelta(days=365)
            start_date = st.date_input("Start date", value=default_start)
        with col_d2:
            end_date = st.date_input("End date", value=datetime.today())

    if start_date > end_date:
        st.error("Start date must be before end date.", icon=":material/warning:")
        st.stop()

    ticker = ticker_input
    if market_choice == "Indian market (NSE)" and ticker and not ticker.endswith(".NS"):
        ticker = f"{ticker}.NS"
    currency_symbol = "₹" if ticker.endswith(".NS") else "$"

    if ticker:
        with st.spinner(f"Loading data for {ticker}..."):
            df = load_stock_data(ticker, start_date, end_date, interval_choice)

        if df.empty:
            st.warning(f"No stock data found for '{ticker}'. Please check the symbol and dates.", icon=":material/warning:")
        else:
            latest_row = df.iloc[-1]
            prev_row   = df.iloc[-2] if len(df) > 1 else None
            lc = float(latest_row['Close'])
            lo = float(latest_row['Open'])
            lh = float(latest_row['High'])
            ll = float(latest_row['Low'])
            lv = float(latest_row['Volume'])
            pc = lc - float(prev_row['Close']) if prev_row is not None else 0.0
            pp = (pc / (abs(float(prev_row['Close'])) + 1e-9) * 100) if prev_row is not None else 0.0

            m1, m2, m3, m4, m5 = st.columns(5)
            with m1: st.metric("Latest close", f"{currency_symbol}{lc:,.2f}", delta=f"{pc:+,.2f} ({pp:+.2f}%)" if prev_row is not None else None)
            with m2: st.metric("Open",   f"{currency_symbol}{lo:,.2f}")
            with m3: st.metric("High",   f"{currency_symbol}{lh:,.2f}")
            with m4: st.metric("Low",    f"{currency_symbol}{ll:,.2f}")
            with m5: st.metric("Volume", format_volume(lv))

            st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)

            if nav_choice == "Data Downloader":
                st.subheader("Data preview & export")
                df_exp = df.copy().reset_index()
                if 'Date' in df_exp.columns:
                    df_exp['Date'] = df_exp['Date'].dt.strftime('%Y-%m-%d')
                elif 'Datetime' in df_exp.columns:
                    df_exp.rename(columns={'Datetime': 'Date'}, inplace=True)
                    df_exp['Date'] = pd.to_datetime(df_exp['Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
                for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
                    if col in df_exp.columns: df_exp[col] = df_exp[col].round(4)
                if 'Volume' in df_exp.columns: df_exp['Volume'] = df_exp['Volume'].astype(int)
                
                st.dataframe(df_exp.sort_values(by='Date', ascending=False), width="stretch")
                st.download_button("📥 Download as CSV",
                    data=df_exp.to_csv(index=False).encode(),
                    file_name=f"{ticker}_{interval_choice.lower()}_data.csv",
                    mime="text/csv", key="dl-csv", width="stretch")

            elif nav_choice == "Charts":
                chart_template = 'plotly_dark' if dark_theme else 'plotly_white'
                grid_color = '#2C2C2E' if dark_theme else '#E8E8ED'
                line_color = '#3A3A3C' if dark_theme else '#D2D2D7'
                text_color = '#F2F2F7' if dark_theme else '#1D1D1F'

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.75, 0.25])
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price',
                    increasing_line_color='#34C759', decreasing_line_color='#FF3B30', increasing_fillcolor='#34C759', decreasing_fillcolor='#FF3B30'
                ), row=1, col=1)
                if len(df) >= 20:
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), line=dict(color='#0066cc', width=1.5), name='20 SMA'), row=1, col=1)
                vol_c = ['#34C759' if c >= o else '#FF3B30' for c, o in zip(df['Close'], df['Open'])]
                fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_c, name='Volume', opacity=0.8), row=2, col=1)
                fig.update_layout(
                    xaxis_rangeslider_visible=False, xaxis2_rangeslider_visible=False, height=520, margin=dict(t=10, b=10, l=45, r=45),
                    template=chart_template, hovermode='x unified', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color=text_color),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                for r in [1, 2]:
                    fig.update_xaxes(showgrid=True, gridcolor=grid_color, linecolor=line_color, row=r, col=1)
                fig.update_yaxes(title_text=f"Price ({'INR' if ticker.endswith('.NS') else 'USD'})", showgrid=True, gridcolor=grid_color, linecolor=line_color, row=1, col=1)
                fig.update_yaxes(title_text="Volume", showgrid=True, gridcolor=grid_color, linecolor=line_color, row=2, col=1)
                st.plotly_chart(fig, use_container_width=True)

# --- MULTI-TICKER SCREENER & STRATEGY BUILDER ---
elif nav_choice in ["Screener", "Strategy"]:
    st.markdown(f'<div class="main-title">{nav_choice}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Scan stock indices and custom parameters dynamically.</div>', unsafe_allow_html=True)

    if "screener_tickers" not in st.session_state:
        st.session_state.screener_tickers = NIFTY50_TICKERS

    # Presets section
    st.markdown("<p class='section-label'>Index Presets</p>", unsafe_allow_html=True)
    ip1, ip2 = st.columns(2)
    with ip1:
        if st.button("Nifty 50 (all 50 stocks)", width="stretch", key="preset_n50"):
            st.session_state.screener_tickers = NIFTY50_TICKERS
            st.rerun()
    with ip2:
        if st.button("Nifty 500 (full list)", width="stretch", key="preset_n500"):
            st.session_state.screener_tickers = NIFTY500_TICKERS
            st.rerun()

    st.markdown("<p class='section-label' style='margin-top:10px'>Indian Sector Watchlists</p>", unsafe_allow_html=True)
    sec_cols = st.columns(4)
    for idx, (label, val) in enumerate(SECTOR_PRESETS.items()):
        with sec_cols[idx % 4]:
            if st.button(label, width="stretch", key=f"preset_{label}"):
                st.session_state.screener_tickers = val
                st.rerun()

    col_t, col_tf = st.columns([6, 4])
    with col_t:
        ticker_input_screener = st.text_input(
            "Tickers to scan (comma separated)", key="screener_tickers",
            help="Append .NS for Indian NSE stocks. e.g. RELIANCE.NS, TCS.NS")
    with col_tf:
        screener_interval = st.segmented_control(
            "Screener Timeframe",
            options=["Daily", "Weekly", "Monthly"],
            default="Daily",
            key="screener_tf_choice"
        )
        if not screener_interval:
            screener_interval = "Daily"

    # Indicator Configurations
    st.markdown("<p class='section-label'>Indicator parameters</p>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("**Trend & Moving Averages**")
        rA1, rA2, rA3, rA4 = st.columns(4)
        with rA1:
            enable_ema = st.toggle("EMA", value=True, key="tog_ema")
            ema_raw = st.text_input("EMA Periods (comma-sep)", "10, 21, 50, 200", key="cfg_ema") if enable_ema else "10, 21, 50, 200"
        with rA2:
            enable_sma = st.toggle("SMA", value=True, key="tog_sma")
            sma_raw = st.text_input("SMA Periods (comma-sep)", "20, 50, 200", key="cfg_sma") if enable_sma else "20, 50, 200"
        with rA3:
            enable_adx = st.toggle("ADX + ±DI", value=True, key="tog_adx")
            adx_period = st.number_input("ADX period", 2, 100, 14, key="cfg_adx") if enable_adx else 14
        with rA4:
            enable_vwap = st.toggle("VWAP", value=False, key="tog_vwap")

        st.divider()
        st.markdown("**Momentum**")
        rB1, rB2, rB3, rB4 = st.columns(4)
        with rB1:
            enable_rsi = st.toggle("RSI", value=True, key="tog_rsi")
            rsi_period = st.number_input("RSI period", 2, 100, 14, key="cfg_rsi") if enable_rsi else 14
        with rB2:
            enable_stoch = st.toggle("Stochastic %K/%D", value=False, key="tog_stoch")
            if enable_stoch:
                stoch_k = st.number_input("Stoch %K period", 2, 100, 14, key="cfg_stoch_k")
                stoch_d = st.number_input("Stoch %D period", 2, 100, 3,  key="cfg_stoch_d")
            else:
                stoch_k, stoch_d = 14, 3
        with rB3:
            enable_cci = st.toggle("CCI", value=False, key="tog_cci")
            cci_period = st.number_input("CCI period", 2, 100, 20, key="cfg_cci") if enable_cci else 20
        with rB4:
            enable_roc = st.toggle("ROC", value=False, key="tog_roc")
            roc_period = st.number_input("ROC period", 2, 200, 10, key="cfg_roc") if enable_roc else 10

        st.divider()
        st.markdown("**MACD & Volatility**")
        rC1, rC2, rC3, rC4 = st.columns(4)
        with rC1:
            enable_macd = st.toggle("MACD", value=True, key="tog_macd")
            if enable_macd:
                macd_fast = st.number_input("Fast",   2, 100, 12, key="cfg_macd_f")
                macd_slow = st.number_input("Slow",   2, 200, 26, key="cfg_macd_s")
                macd_sig  = st.number_input("Signal", 2, 100,  9, key="cfg_macd_sig")
            else:
                macd_fast, macd_slow, macd_sig = 12, 26, 9
        with rC2:
            enable_bb = st.toggle("Bollinger Bands", value=False, key="tog_bb")
            bb_period = st.number_input("BB period", 2, 200, 20, key="cfg_bb") if enable_bb else 20
        with rC3:
            enable_atr = st.toggle("ATR", value=False, key="tog_atr")
            atr_period = st.number_input("ATR period", 2, 100, 14, key="cfg_atr") if enable_atr else 14
        with rC4:
            enable_willr = st.toggle("Williams %R", value=False, key="tog_willr")
            willr_period = st.number_input("Williams %R period", 2, 100, 14, key="cfg_willr") if enable_willr else 14

        st.divider()
        st.markdown("**Volume**")
        rD1, rD2, _, _ = st.columns(4)
        with rD1:
            enable_obv = st.toggle("OBV", value=False, key="tog_obv")
        with rD2:
            enable_mfi = st.toggle("MFI", value=False, key="tog_mfi")
            mfi_period = st.number_input("MFI period", 2, 100, 14, key="cfg_mfi") if enable_mfi else 14

    ema_periods = parse_periods(ema_raw, [10, 21, 50, 200]) if enable_ema else []
    sma_periods = parse_periods(sma_raw, [20, 50, 200])     if enable_sma else []

    screener_cfg = dict(
        enable_ema=enable_ema, ema_periods=ema_periods,
        enable_sma=enable_sma, sma_periods=sma_periods,
        enable_rsi=enable_rsi, rsi_period=int(rsi_period),
        enable_adx=enable_adx, adx_period=int(adx_period),
        enable_macd=enable_macd, macd_fast=int(macd_fast),
            macd_slow=int(macd_slow), macd_signal=int(macd_sig),
        enable_bb=enable_bb, bb_period=int(bb_period),
        enable_stoch=enable_stoch, stoch_k=int(stoch_k), stoch_d=int(stoch_d),
        enable_atr=enable_atr, atr_period=int(atr_period),
        enable_cci=enable_cci, cci_period=int(cci_period),
        enable_willr=enable_willr, willr_period=int(willr_period),
        enable_vwap=enable_vwap,
        enable_obv=enable_obv,
        enable_mfi=enable_mfi, mfi_period=int(mfi_period),
        enable_roc=enable_roc, roc_period=int(roc_period),
    )

    if st.button(":material/radar: Run Scan & Compute Technicals", type="primary", width="stretch", key="run-screener"):
        tickers_list = [t.strip().upper() for t in ticker_input_screener.split(",") if t.strip()]
        if not tickers_list:
            st.warning("Enter at least one ticker.", icon=":material/warning:")
        else:
            with st.spinner(f"Downloading historical data for {len(tickers_list)} tickers..."):
                df_raw = load_screener_data(tuple(sorted(tickers_list)), screener_interval)
            if df_raw.empty:
                st.error("No stock data could be downloaded.", icon=":material/error:")
            else:
                results = []
                prog = st.progress(0, text="Analyzing stocks...")
                for i, t in enumerate(tickers_list):
                    tdf = pd.DataFrame(index=df_raw.index)
                    for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                        if isinstance(df_raw.columns, pd.MultiIndex):
                            if (col, t) in df_raw.columns: tdf[col] = df_raw[(col, t)]
                        else:
                            if col in df_raw.columns: tdf[col] = df_raw[col]
                    tdf = tdf.dropna(subset=['Close'])
                    if len(tdf) >= 14:
                        res = screen_ticker(tdf, screener_cfg)
                        if res:
                            res["Ticker"] = t
                            results.append(res)
                    prog.progress((i + 1) / len(tickers_list))
                prog.empty()
                if results:
                    rdf = pd.DataFrame(results)
                    rdf = rdf[["Ticker"] + [c for c in rdf.columns if c != "Ticker"]]
                    st.session_state.screener_raw_df = rdf
                    st.session_state.screener_cfg_snap = screener_cfg
                    st.session_state.pop("strategy_results_df", None)
                    st.success(f"Successfully computed parameters for {len(results)} stocks!", icon=":material/check_circle:")
                else:
                    st.warning("No valid computed details for scanned list.", icon=":material/warning:")

    # --- SCREENER DISPLAY VIEW ---
    if nav_choice == "Screener" and "screener_raw_df" in st.session_state:
        snap = st.session_state.get("screener_cfg_snap", screener_cfg)
        raw_df = st.session_state.screener_raw_df.copy()
        all_cols = list(raw_df.columns)

        st.divider()
        st.markdown("<p class='section-label'>Quick Filters</p>", unsafe_allow_html=True)
        with st.container(border=True):
            qf1, qf2, qf3, qf4 = st.columns(4)
            rsi_col = f"RSI {snap['rsi_period']}" if snap["enable_rsi"] else None
            with qf1:
                rsi_qf = st.selectbox("RSI Position", ["All", "Oversold (< 30)", "Neutral (30–70)", "Overbought (> 70)", "Custom range"], disabled=(rsi_col is None or rsi_col not in raw_df.columns))
                rsi_range = st.slider("RSI Custom Range Slider", 0, 100, (20, 80), key="rsi_qf_slider") if rsi_qf == "Custom range" else (0, 100)

            adx_col = f"ADX {snap['adx_period']}" if snap["enable_adx"] else None
            with qf2:
                adx_qf = st.selectbox("ADX Trend Strength", ["All", "Strong (> 25)", "Moderate (20–25)", "Weak (< 20)"], disabled=(adx_col is None or adx_col not in raw_df.columns))

            ema_cols = [c for c in all_cols if c.startswith("EMA ")]
            with qf3:
                ema_qf_opts = ["All"] + [f"Close > {c}" for c in ema_cols] + [f"Close < {c}" for c in ema_cols] + [f"Close == {c}" for c in ema_cols]
                ema_qf = st.selectbox("EMA Strategy Positioning", ema_qf_opts, disabled=(not ema_cols))

            with qf4:
                vol_qf = st.selectbox("Daily Volume Cutoff", ["All", "> 100K", "> 500K", "> 1M", "> 5M", "> 10M"])

            qf5, qf6, _, _ = st.columns(4)
            with qf5:
                high52_qf = st.selectbox("52W High Proximity Range", ["All", "Within 5% of 52W High", "Within 10% of 52W High", "Within 20% of 52W High", "At / above 52W High (≥ 0%)", "Below 52W High > 20%"])
            with qf6:
                volchg_qf = st.selectbox("Volume vs 20D Average", ["All", "Vol surge > 50%", "Vol surge > 100%", "Vol surge > 200%", "Vol dry-up < -30%", "Vol dry-up < -50%"])

        fdf = raw_df.copy()
        if rsi_col and rsi_col in fdf.columns:
            if rsi_qf == "Oversold (< 30)":     fdf = fdf[fdf[rsi_col] < 30]
            elif rsi_qf == "Neutral (30–70)":   fdf = fdf[(fdf[rsi_col] >= 30) & (fdf[rsi_col] <= 70)]
            elif rsi_qf == "Overbought (> 70)": fdf = fdf[fdf[rsi_col] > 70]
            elif rsi_qf == "Custom range":      fdf = fdf[(fdf[rsi_col] >= rsi_range[0]) & (fdf[rsi_col] <= rsi_range[1])]

        if adx_col and adx_col in fdf.columns:
            if adx_qf == "Strong (> 25)":       fdf = fdf[fdf[adx_col] > 25]
            elif adx_qf == "Moderate (20–25)":  fdf = fdf[(fdf[adx_col] >= 20) & (fdf[adx_col] <= 25)]
            elif adx_qf == "Weak (< 20)":       fdf = fdf[fdf[adx_col] < 20]

        if ema_qf != "All" and " " in ema_qf:
            parts = ema_qf.split(" ")
            ema_c = f"{parts[2]} {parts[3]}"
            if ema_c in fdf.columns:
                if parts[1] == ">":     fdf = fdf[fdf["Close"] > fdf[ema_c]]
                elif parts[1] == "<":   fdf = fdf[fdf["Close"] < fdf[ema_c]]
                elif parts[1] == "==":  fdf = fdf[fdf["Close"].round(2) == fdf[ema_c].round(2)]

        vol_map = {"> 100K": 1e5, "> 500K": 5e5, "> 1M": 1e6, "> 5M": 5e6, "> 10M": 1e7}
        if vol_qf in vol_map:
            fdf = fdf[fdf["Volume"] > vol_map[vol_qf]]

        if high52_qf != "All" and "% from 52W High" in fdf.columns:
            if high52_qf == "Within 5% of 52W High":         fdf = fdf[fdf["% from 52W High"] >= -5]
            elif high52_qf == "Within 10% of 52W High":       fdf = fdf[fdf["% from 52W High"] >= -10]
            elif high52_qf == "Within 20% of 52W High":       fdf = fdf[fdf["% from 52W High"] >= -20]
            elif high52_qf == "At / above 52W High (≥ 0%)":  fdf = fdf[fdf["% from 52W High"] >= 0]
            elif high52_qf == "Below 52W High > 20%":         fdf = fdf[fdf["% from 52W High"] < -20]

        if volchg_qf != "All" and "Vol vs 20D Avg %" in fdf.columns:
            if volchg_qf == "Vol surge > 50%":        fdf = fdf[fdf["Vol vs 20D Avg %"] > 50]
            elif volchg_qf == "Vol surge > 100%":     fdf = fdf[fdf["Vol vs 20D Avg %"] > 100]
            elif volchg_qf == "Vol surge > 200%":     fdf = fdf[fdf["Vol vs 20D Avg %"] > 200]
            elif volchg_qf == "Vol dry-up < -30%":    fdf = fdf[fdf["Vol vs 20D Avg %"] < -30]
            elif volchg_qf == "Vol dry-up < -50%":    fdf = fdf[fdf["Vol vs 20D Avg %"] < -50]

        st.caption(f"Filtered Results: **{len(fdf)}** matching out of **{len(raw_df)}** stocks.")
        st.dataframe(fdf, width="stretch")
        st.download_button("📥 Download Filtered Scan Results", data=fdf.to_csv(index=False).encode(), file_name=f"screener_scan.csv", mime="text/csv", key="dl-scan", width="stretch")

    # --- STRATEGY BUILDER DISPLAY VIEW ---
    elif nav_choice == "Strategy" and "screener_raw_df" in st.session_state:
        snap = st.session_state.get("screener_cfg_snap", screener_cfg)
        raw_df = st.session_state.screener_raw_df.copy()
        
        st.divider()
        numeric_cols = [c for c in raw_df.columns if raw_df[c].dtype in [float, np.float64, np.float32]]
        
        if not numeric_cols:
            st.info("Run the scan first to load parameters.", icon=":material/info:")
        else:
            # Main Strategy configurations
            strategy_name = st.text_input("Strategy Name / Title", value="My Custom Strategy", key="strat_name")
            if "strat_sl_val" not in st.session_state:
                st.session_state.strat_sl_val = 5.0
            stop_loss_val = st.number_input("Stop Loss % (SL)", min_value=0.0, max_value=100.0, key="strat_sl_val", step=0.1, help="Max loss % allowed from entry. Set to 0 to disable.")

            st.divider()
            # ── ENTRY CONDITIONS BUILDER ──
            st.subheader("1. Entry Conditions")
            entry_match = st.segmented_control("Entry logic match mode", options=["AND (all must match)", "OR (any must match)"], default="AND (all must match)", key="strat_entry_mode")
            if not entry_match: entry_match = "AND (all must match)"

            if "strategy_entry_conditions" not in st.session_state:
                st.session_state.strategy_entry_conditions = [
                    {"lhs_col": numeric_cols[0], "op": ">", "rhs_type": "Value", "rhs_val": 0.0, "rhs_col": numeric_cols[0]}
                ]

            eb1, eb2 = st.columns([1, 1])
            with eb1:
                if st.button("➕ Add Entry Condition", key="entry_add"):
                    st.session_state.strategy_entry_conditions.append(
                        {"lhs_col": numeric_cols[0], "op": ">", "rhs_type": "Value", "rhs_val": 0.0, "rhs_col": numeric_cols[0]}
                    )
                    st.rerun()
            with eb2:
                if st.button("🗑️ Clear Entry List", key="entry_clear"):
                    st.session_state.strategy_entry_conditions = [
                        {"lhs_col": numeric_cols[0], "op": ">", "rhs_type": "Value", "rhs_val": 0.0, "rhs_col": numeric_cols[0]}
                    ]
                    st.rerun()

            entry_delete = []
            for idx, cond in enumerate(st.session_state.strategy_entry_conditions):
                with st.container(border=True):
                    rcols = st.columns([3, 1.5, 1.5, 3, 0.8])
                    with rcols[0]:
                        lhs = st.selectbox(f"Entry_LHS_{idx}", numeric_cols, index=numeric_cols.index(cond["lhs_col"]) if cond["lhs_col"] in numeric_cols else 0, key=f"e_lhs_{idx}", label_visibility="collapsed")
                    with rcols[1]:
                        op = st.selectbox(f"Entry_OP_{idx}", OPERATORS, index=OPERATORS.index(cond["op"]) if cond["op"] in OPERATORS else 0, key=f"e_op_{idx}", label_visibility="collapsed")
                    with rcols[2]:
                        rhs_type = st.segmented_control(
                            "RHS Type",
                            options=["Value", "Column"],
                            default=cond.get("rhs_type", "Value"),
                            key=f"e_rhs_type_{idx}",
                            label_visibility="collapsed"
                        )
                        if not rhs_type: rhs_type = "Value"
                    with rcols[3]:
                        if rhs_type == "Value":
                            rhs_val = st.number_input(f"Entry_RHSVal_{idx}", value=float(cond.get("rhs_val", 0.0)), key=f"e_rhs_val_{idx}", label_visibility="collapsed", format="%.2f")
                            rhs_col = cond.get("rhs_col", numeric_cols[0])
                        else:
                            rhs_col = st.selectbox(f"Entry_RHSCol_{idx}", numeric_cols, index=numeric_cols.index(cond["rhs_col"]) if cond.get("rhs_col") in numeric_cols else 0, key=f"e_rhs_col_{idx}", label_visibility="collapsed")
                            rhs_val = 0.0
                    with rcols[4]:
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"e_del_{idx}"):
                            entry_delete.append(idx)
                    st.session_state.strategy_entry_conditions[idx] = {
                        "lhs_col": lhs, "op": op, "rhs_type": rhs_type, "rhs_val": rhs_val, "rhs_col": rhs_col
                    }

            if entry_delete:
                for d_idx in sorted(entry_delete, reverse=True):
                    st.session_state.strategy_entry_conditions.pop(d_idx)
                st.rerun()

            st.divider()
            # ── EXIT CONDITIONS BUILDER ──
            st.subheader("2. Exit Conditions")
            exit_match = st.segmented_control("Exit logic match mode", options=["AND (all must match)", "OR (any must match)"], default="AND (all must match)", key="strat_exit_mode")
            if not exit_match: exit_match = "AND (all must match)"

            if "strategy_exit_conditions" not in st.session_state:
                st.session_state.strategy_exit_conditions = [
                    {"lhs_col": numeric_cols[0], "op": "<", "rhs_type": "Value", "rhs_val": 0.0, "rhs_col": numeric_cols[0]}
                ]

            exb1, exb2 = st.columns([1, 1])
            with exb1:
                if st.button("➕ Add Exit Condition", key="exit_add"):
                    st.session_state.strategy_exit_conditions.append(
                        {"lhs_col": numeric_cols[0], "op": "<", "rhs_type": "Value", "rhs_val": 0.0, "rhs_col": numeric_cols[0]}
                    )
                    st.rerun()
            with exb2:
                if st.button("🗑️ Clear Exit List", key="exit_clear"):
                    st.session_state.strategy_exit_conditions = [
                        {"lhs_col": numeric_cols[0], "op": "<", "rhs_type": "Value", "rhs_val": 0.0, "rhs_col": numeric_cols[0]}
                    ]
                    st.rerun()

            exit_delete = []
            for idx, cond in enumerate(st.session_state.strategy_exit_conditions):
                with st.container(border=True):
                    rcols = st.columns([3, 1.5, 1.5, 3, 0.8])
                    with rcols[0]:
                        lhs = st.selectbox(f"Exit_LHS_{idx}", numeric_cols, index=numeric_cols.index(cond["lhs_col"]) if cond["lhs_col"] in numeric_cols else 0, key=f"ex_lhs_{idx}", label_visibility="collapsed")
                    with rcols[1]:
                        op = st.selectbox(f"Exit_OP_{idx}", OPERATORS, index=OPERATORS.index(cond["op"]) if cond["op"] in OPERATORS else 0, key=f"ex_op_{idx}", label_visibility="collapsed")
                    with rcols[2]:
                        rhs_type = st.segmented_control(
                            "RHS Type",
                            options=["Value", "Column"],
                            default=cond.get("rhs_type", "Value"),
                            key=f"ex_rhs_type_{idx}",
                            label_visibility="collapsed"
                        )
                        if not rhs_type: rhs_type = "Value"
                    with rcols[3]:
                        if rhs_type == "Value":
                            rhs_val = st.number_input(f"Exit_RHSVal_{idx}", value=float(cond.get("rhs_val", 0.0)), key=f"ex_rhs_val_{idx}", label_visibility="collapsed", format="%.2f")
                            rhs_col = cond.get("rhs_col", numeric_cols[0])
                        else:
                            rhs_col = st.selectbox(f"Exit_RHSCol_{idx}", numeric_cols, index=numeric_cols.index(cond["rhs_col"]) if cond.get("rhs_col") in numeric_cols else 0, key=f"ex_col_{idx}", label_visibility="collapsed")
                            rhs_val = 0.0
                    with rcols[4]:
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"ex_del_{idx}"):
                            exit_delete.append(idx)
                    st.session_state.strategy_exit_conditions[idx] = {
                        "lhs_col": lhs, "op": op, "rhs_type": rhs_type, "rhs_val": rhs_val, "rhs_col": rhs_col
                    }

            if exit_delete:
                for d_idx in sorted(exit_delete, reverse=True):
                    st.session_state.strategy_exit_conditions.pop(d_idx)
                st.rerun()

            st.divider()

            # 💾 Save strategy configuration
            if st.button("💾 Save Strategy to Library", type="secondary", width="stretch", key="save_full_strat"):
                clean_name = strategy_name.strip()
                if not clean_name:
                    st.error("Strategy Title is empty.", icon=":material/error:")
                else:
                    success = save_custom_strategy(
                        clean_name,
                        st.session_state.strategy_entry_conditions,
                        st.session_state.strategy_exit_conditions,
                        stop_loss_val,
                        entry_match,
                        exit_match,
                        screener_cfg
                    )
                    if success:
                        st.toast(f"Strategy '{clean_name}' saved to library successfully!")

            # ⚡ Test strategy against current scan
            if st.button("⚡ Test Scan Current Stocks (Check Signals)", type="primary", width="stretch", key="test_strat_scan"):
                # Apply strategy logic to latest row
                entry_mask_current = apply_strategy(raw_df.copy(), st.session_state.strategy_entry_conditions, entry_match)
                exit_mask_current  = apply_strategy(raw_df.copy(), st.session_state.strategy_exit_conditions, exit_match)
                
                results_df = raw_df.copy()
                results_df["Signal Status"] = "HOLD / NEUTRAL"
                results_df.loc[results_df["Ticker"].isin(entry_mask_current["Ticker"]), "Signal Status"] = "BUY / ENTRY 🟢"
                results_df.loc[results_df["Ticker"].isin(exit_mask_current["Ticker"]), "Signal Status"] = "SELL / EXIT 🔴"
                
                st.session_state.strategy_results_df = results_df
                st.session_state.strategy_name = strategy_name

            if "strategy_results_df" in st.session_state:
                sdf = st.session_state.strategy_results_df
                sname = st.session_state.get("strategy_name", "strategy")
                st.subheader(f"Strategy Signal Scanner — {sname}")
                st.dataframe(sdf, width="stretch")
                
                csv_matched = sdf.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Export scan CSV", data=csv_matched, file_name=f"{sname.replace(' ', '_').lower()}_latest_signals.csv", mime="text/csv", key="dl-strat-latest", width="stretch")
    else:
        st.info("Run the scan above to populate indicators, then choose parameters or custom strategy rules.", icon=":material/info:")

# --- SAVED STRATEGIES LIBRARY VIEW ---
elif nav_choice == "Saved Strategies":
    st.markdown('<div class="main-title">Saved Strategies</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Select, run, and evaluate your saved custom strategy library.</div>', unsafe_allow_html=True)

    library = load_saved_strategies()

    if not library:
        st.info("Your custom strategy library is empty.", icon=":material/info:")
    else:
        strat_names = list(library.keys())
        selected_strat_name = st.selectbox("Choose a saved strategy", options=strat_names)
        strat_info = library[selected_strat_name]
        
        with st.container(border=True):
            st.markdown(f"### Strategy: **{selected_strat_name}**")
            st.caption(f"Created/Saved on: {strat_info.get('created_at', 'N/A')}")
            st.divider()
            
            e_conds = strat_info.get("entry_conditions", strat_info.get("conditions", []))
            ex_conds = strat_info.get("exit_conditions", [])
            sl_val   = strat_info.get("stop_loss_pct", 5.0)
            e_mm = strat_info.get("entry_match_mode", "AND")
            ex_mm = strat_info.get("exit_match_mode", "AND")
            
            st.markdown(f"**Stop Loss %**: `{sl_val}%` from entry price.")
            
            # Print entry conditions
            e_parts = []
            for c in e_conds:
                rhs_val = f"{c['rhs_val']:.2f}" if c.get("rhs_type", "Value") == "Value" else c.get("rhs_col", "")
                e_parts.append(f"`{c['lhs_col']}` {c['op']} {rhs_val}")
            st.markdown(f"**Entry Signals Formula**: {(' ' + (' AND ' if 'AND' in e_mm else ' OR ') + ' ').join(e_parts) if e_parts else 'None'}")
            
            # Print exit conditions
            ex_parts = []
            for c in ex_conds:
                rhs_val = f"{c['rhs_val']:.2f}" if c.get("rhs_type", "Value") == "Value" else c.get("rhs_col", "")
                ex_parts.append(f"`{c['lhs_col']}` {c['op']} {rhs_val}")
            st.markdown(f"**Exit Signals Formula**: {(' ' + (' AND ' if 'AND' in ex_mm else ' OR ') + ' ').join(ex_parts) if ex_parts else 'None'}")

        # Choose Watchlist for Scan
        st.markdown("<p class='section-label'>Target Scan Watchlist</p>", unsafe_allow_html=True)
        col_w, col_wf = st.columns([6, 4])
        with col_w:
            wl_preset = st.radio("Choose Watchlist Profile", options=["Nifty 50 Preset", "Nifty 500 Preset", "Custom list of tickers"], horizontal=True)
        with col_wf:
            saved_strat_interval = st.segmented_control(
                "Timeframe",
                options=["Daily", "Weekly", "Monthly"],
                default="Daily",
                key="saved_strat_tf_choice"
            )
            if not saved_strat_interval:
                saved_strat_interval = "Daily"
        
        if wl_preset == "Nifty 50 Preset":
            ticker_list_raw = NIFTY50_TICKERS
        elif wl_preset == "Nifty 500 Preset":
            ticker_list_raw = NIFTY500_TICKERS
        else:
            ticker_list_raw = st.text_input("Enter custom comma-separated tickers", value="AAPL, MSFT, RELIANCE.NS, TCS.NS")

        c_del, c_edit, c_run = st.columns([2, 2, 6])
        with c_del:
            if st.button("🗑️ Delete Strategy", width="stretch", key="del-strat-btn"):
                if delete_custom_strategy(selected_strat_name):
                    st.toast(f"Strategy '{selected_strat_name}' deleted successfully!")
                    st.rerun()
        with c_edit:
            if st.button("🖊️ Edit Strategy", width="stretch", key="edit-strat-btn"):
                st.session_state.strategy_entry_conditions = strat_info.get("entry_conditions", strat_info.get("conditions", []))
                st.session_state.strategy_exit_conditions = strat_info.get("exit_conditions", [])
                st.session_state.strat_name = selected_strat_name
                st.session_state.strat_sl_val = float(strat_info.get("stop_loss_pct", 5.0))
                
                e_mode = strat_info.get("entry_match_mode", "AND")
                st.session_state.strat_entry_mode = "AND (all must match)" if "AND" in e_mode else "OR (any must match)"
                
                ex_mode = strat_info.get("exit_match_mode", "AND")
                st.session_state.strat_exit_mode = "AND (all must match)" if "AND" in ex_mode else "OR (any must match)"
                
                cfg = strat_info.get("cfg", {})
                if cfg:
                    st.session_state.tog_ema = cfg.get("enable_ema", True)
                    st.session_state.cfg_ema = ", ".join(map(str, cfg.get("ema_periods", [10, 21, 50, 200])))
                    st.session_state.tog_sma = cfg.get("enable_sma", True)
                    st.session_state.cfg_sma = ", ".join(map(str, cfg.get("sma_periods", [20, 50, 200])))
                    st.session_state.tog_rsi = cfg.get("enable_rsi", True)
                    st.session_state.cfg_rsi = cfg.get("rsi_period", 14)
                    st.session_state.tog_adx = cfg.get("enable_adx", True)
                    st.session_state.cfg_adx = cfg.get("adx_period", 14)
                    st.session_state.tog_macd = cfg.get("enable_macd", True)
                    st.session_state.cfg_macd_f = cfg.get("macd_fast", 12)
                    st.session_state.cfg_macd_s = cfg.get("macd_slow", 26)
                    st.session_state.cfg_macd_sig = cfg.get("macd_signal", 9)
                    st.session_state.tog_bb = cfg.get("enable_bb", False)
                    st.session_state.cfg_bb = cfg.get("bb_period", 20)
                    st.session_state.tog_stoch = cfg.get("enable_stoch", False)
                    st.session_state.cfg_stoch_k = cfg.get("stoch_k", 14)
                    st.session_state.cfg_stoch_d = cfg.get("stoch_d", 3)
                    st.session_state.tog_atr = cfg.get("enable_atr", False)
                    st.session_state.cfg_atr = cfg.get("atr_period", 14)
                    st.session_state.tog_cci = cfg.get("enable_cci", False)
                    st.session_state.cfg_cci = cfg.get("cci_period", 20)
                    st.session_state.tog_willr = cfg.get("enable_willr", False)
                    st.session_state.cfg_willr = cfg.get("willr_period", 14)
                    st.session_state.tog_vwap = cfg.get("enable_vwap", False)
                    st.session_state.tog_obv = cfg.get("enable_obv", False)
                    st.session_state.tog_mfi = cfg.get("enable_mfi", False)
                    st.session_state.cfg_mfi = cfg.get("mfi_period", 14)
                    st.session_state.tog_roc = cfg.get("enable_roc", False)
                    st.session_state.cfg_roc = cfg.get("roc_period", 10)
                
                st.session_state.edit_load_requested = True
                st.rerun()
        with c_run:
            run_clicked = st.button("⚡ Run Saved Strategy Scan", type="primary", width="stretch", key="run-saved-strat-btn")

        if run_clicked:
            target_tickers = [t.strip().upper() for t in ticker_list_raw.split(",") if t.strip()]
            if not target_tickers:
                st.warning("Please enter at least one target stock ticker.")
            else:
                with st.spinner("Downloading data for selected stocks..."):
                    df_raw = load_screener_data(tuple(sorted(target_tickers)), saved_strat_interval)
                
                if df_raw.empty:
                    st.error("Failed to retrieve price data.", icon=":material/error:")
                else:
                    results = []
                    prog = st.progress(0, text="Calculating indicator math...")
                    saved_cfg = strat_info.get("cfg", {})
                    
                    for i, t in enumerate(target_tickers):
                        tdf = pd.DataFrame(index=df_raw.index)
                        for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                            if isinstance(df_raw.columns, pd.MultiIndex):
                                if (col, t) in df_raw.columns: tdf[col] = df_raw[(col, t)]
                            else:
                                if col in df_raw.columns: tdf[col] = df_raw[col]
                        tdf = tdf.dropna(subset=['Close'])
                        if len(tdf) >= 14:
                            res = screen_ticker(tdf, saved_cfg)
                            if res:
                                res["Ticker"] = t
                                results.append(res)
                        prog.progress((i + 1) / len(target_tickers))
                    prog.empty()
                    
                    if results:
                        rdf = pd.DataFrame(results)
                        rdf = rdf[["Ticker"] + [c for c in rdf.columns if c != "Ticker"]]
                        
                        entry_mask_current = apply_strategy(rdf.copy(), e_conds, e_mm)
                        exit_mask_current  = apply_strategy(rdf.copy(), ex_conds, ex_mm)
                        
                        rdf["Signal Status"] = "HOLD / NEUTRAL"
                        rdf.loc[rdf["Ticker"].isin(entry_mask_current["Ticker"]), "Signal Status"] = "BUY / ENTRY 🟢"
                        rdf.loc[rdf["Ticker"].isin(exit_mask_current["Ticker"]), "Signal Status"] = "SELL / EXIT 🔴"
                        
                        st.subheader(f"Strategy Scan Signals")
                        st.dataframe(rdf, width="stretch")
                        
                        csv_matched = rdf.to_csv(index=False).encode('utf-8')
                        st.download_button(label=f"📥 Download matches for '{selected_strat_name}'", data=csv_matched, file_name=f"{selected_strat_name.replace(' ', '_').lower()}_matches.csv", mime="text/csv", key="dl-saved-strat-res", width="stretch")
                    else:
                        st.warning("No valid indicators could be computed for the targets.")

# --- HISTORICAL BACKTESTING TOOL VIEW ---
elif nav_choice == "Backtester":
    st.markdown('<div class="main-title">Backtester</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Simulate custom strategy rules historically and analyze trade movement statistics.</div>', unsafe_allow_html=True)

    library = load_saved_strategies()

    if not library:
        st.info("No saved strategies found. Create and save a custom strategy in the Strategy builder first!", icon=":material/info:")
    else:
        strat_names = list(library.keys())
        selected_strat_name = st.selectbox("Select Strategy to Backtest", options=strat_names)
        strat_info = library[selected_strat_name]
        
        # Display Formula card
        with st.container(border=True):
            st.markdown(f"### Strategy: **{selected_strat_name}**")
            
            e_conds = strat_info.get("entry_conditions", strat_info.get("conditions", []))
            ex_conds = strat_info.get("exit_conditions", [])
            sl_val   = strat_info.get("stop_loss_pct", 5.0)
            e_mm = strat_info.get("entry_match_mode", "AND")
            ex_mm = strat_info.get("exit_match_mode", "AND")
            
            st.markdown(f"**Stop Loss %**: `{sl_val}%` from entry price.")
            
            e_parts = []
            for c in e_conds:
                rhs_val = f"{c['rhs_val']:.2f}" if c.get("rhs_type", "Value") == "Value" else c.get("rhs_col", "")
                e_parts.append(f"`{c['lhs_col']}` {c['op']} {rhs_val}")
            st.markdown(f"**Entry Signals**: {(' ' + (' AND ' if 'AND' in e_mm else ' OR ') + ' ').join(e_parts) if e_parts else 'None'}")
            
            ex_parts = []
            for c in ex_conds:
                rhs_val = f"{c['rhs_val']:.2f}" if c.get("rhs_type", "Value") == "Value" else c.get("rhs_col", "")
                ex_parts.append(f"`{c['lhs_col']}` {c['op']} {rhs_val}")
            st.markdown(f"**Exit Signals**: {(' ' + (' AND ' if 'AND' in ex_mm else ' OR ') + ' ').join(ex_parts) if ex_parts else 'None'}")

        st.divider()
        st.markdown("<p class='section-label'>Backtest Run Configurations</p>", unsafe_allow_html=True)
        
        col_w, col_tf = st.columns([6, 4])
        with col_w:
            wl_preset = st.radio("Choose Target List Profile", options=["Nifty 50 Preset", "Nifty 500 Preset", "Custom tickers list"], horizontal=True)
        with col_tf:
            backtest_interval = st.segmented_control(
                "Backtest Timeframe",
                options=["Daily", "Weekly", "Monthly"],
                default="Daily",
                key="backtest_tf_choice"
            )
            if not backtest_interval: backtest_interval = "Daily"

        if wl_preset == "Nifty 50 Preset":
            ticker_list_raw = NIFTY50_TICKERS
        elif wl_preset == "Nifty 500 Preset":
            ticker_list_raw = NIFTY500_TICKERS
        else:
            ticker_list_raw = st.text_input("Enter target tickers", value="AAPL, MSFT, RELIANCE.NS, TCS.NS")

        if st.button("⚡ Run Historical Strategy Backtest", type="primary", width="stretch", key="run-backtester"):
            target_tickers = [t.strip().upper() for t in ticker_list_raw.split(",") if t.strip()]
            if not target_tickers:
                st.warning("Enter at least one target stock ticker.")
            else:
                with st.spinner("Downloading 2-year history data for chosen tickers..."):
                    df_raw = load_screener_data(tuple(sorted(target_tickers)), backtest_interval)
                
                if df_raw.empty:
                    st.error("No historical stock data retrieved.", icon=":material/error:")
                else:
                    all_trades = []
                    prog = st.progress(0, text="Backtesting targets...")
                    saved_cfg = strat_info.get("cfg", {})
                    
                    for idx, t in enumerate(target_tickers):
                        tdf = pd.DataFrame(index=df_raw.index)
                        for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                            if isinstance(df_raw.columns, pd.MultiIndex):
                                if (col, t) in df_raw.columns: tdf[col] = df_raw[(col, t)]
                            else:
                                if col in df_raw.columns: tdf[col] = df_raw[col]
                        tdf = tdf.dropna(subset=['Close'])
                        
                        if len(tdf) >= 14:
                            # 1. Compute indicators across timeline
                            history_df = compute_indicators_history(tdf, saved_cfg)
                            
                            # 2. Chronological position simulator
                            sim_trades = run_backtest_simulation(t, history_df, e_conds, ex_conds, sl_val, e_mm, ex_mm)
                            all_trades.extend(sim_trades)
                        
                        prog.progress((idx + 1) / len(target_tickers))
                    prog.empty()
                    
                    if not all_trades:
                        st.info("No trade signals were triggered historically for the selected configurations.", icon=":material/info:")
                    else:
                        trades_df = pd.DataFrame(all_trades)
                        
                        # Compute Summary KPI Metrics
                        total_trades = len(trades_df)
                        winning_trades = len(trades_df[trades_df["Return %"] > 0])
                        win_rate = (winning_trades / total_trades) * 100
                        avg_return = float(trades_df["Return %"].mean())
                        avg_runup  = float(trades_df["Max Run-up %"].mean())
                        avg_drawdown = float(trades_df["Max Drawdown %"].mean())
                        
                        # Compute advanced drawdowns & growth rates
                        dd_metrics = compute_backtest_drawdowns(trades_df, total_period_years=2.0)
                        
                        st.subheader("Backtest Performance Summary")
                        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
                        with kpi1: st.metric("Total Trades", f"{total_trades}")
                        with kpi2: st.metric("Win Rate", f"{win_rate:.1f}%")
                        with kpi3: st.metric("Avg Return", f"{avg_return:+.2f}%")
                        with kpi4: st.metric("CAGR", f"{dd_metrics['cagr_pct']:+.2f}%")
                        with kpi5: st.metric("Calmar Ratio", f"{dd_metrics['calmar']:.2f}")
                        
                        st.markdown("<p class='section-label'>Drawdown & Risk Statistics</p>", unsafe_allow_html=True)
                        with st.container(border=True):
                            dk1, dk2, dk3, dk4 = st.columns(4)
                            with dk1:
                                st.metric("Max Drawdown", f"{dd_metrics['max_dd_pct']:.2f}%")
                                st.caption(f"Max DD Period: **{dd_metrics['max_dd_period']} trades**")
                            with dk2:
                                st.metric("Current Drawdown", f"{dd_metrics['current_dd_pct']:.2f}%")
                                st.caption(f"Current DD Period: **{dd_metrics['current_dd_period']} trades**")
                            with dk3:
                                st.metric("Number of Drawdowns", f"{dd_metrics['num_drawdowns']}")
                            with dk4:
                                st.metric("Mean / Median DD", f"{dd_metrics['mean_dd_pct']:.1f}% / {dd_metrics['median_dd_pct']:.1f}%")
                        
                        st.divider()
                        st.subheader("Simulated Trade Signals Log")
                        st.dataframe(trades_df, width="stretch")
                        
                        csv_trades = trades_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"📥 Download backtest trade logs — {selected_strat_name}",
                            data=csv_trades,
                            file_name=f"{selected_strat_name.replace(' ', '_').lower()}_backtest_results.csv",
                            mime="text/csv",
                            key="dl-backtest-res-btn",
                            width="stretch"
                        )
