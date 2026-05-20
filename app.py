# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════════════════╗
# ║   BİST ULTIMATE QUANT TERMINAL v1.0 — KURUMSAL EDİSYON             ║
# ║   bistv23pro  +  rbta10  FULL MERGE & INTELLIGENCE UPGRADE          ║
# ║                                                                      ║
# ║   [ENGINE A]  curl_cffi Yahoo Chart API — Ban-bypass aktif          ║
# ║   [ENGINE B]  Ensemble AI: XGB + LGBM + CatBoost + RF              ║
# ║   [ENGINE C]  Meta-Labeling Karar Doğrulayıcı                      ║
# ║   [ENGINE D]  Kelly + ATR Volatilite Tabanlı Pozisyon Boyutu       ║
# ║   [ENGINE E]  PSI Drift Monitor — Model Bozulma Koruyucu           ║
# ║   [ENGINE F]  MASTER_SCORE: AI + Teknik + Temel + Akıllı Para      ║
# ║   [MODÜLLER]  Sektörel Rotasyon | Hisse Kartları | Backtest         ║
# ║               Gelişmiş Grafik Stüdyosu | Portföy K/Z Takip         ║
# ║               AI Sinyal Sıralaması | Piyasa Haberleri               ║
# ║   Çalıştır:  streamlit run bist_ultimate_v1.py                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
try:
    from curl_cffi import requests as cffi_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    import requests as cffi_requests
    CURL_CFFI_AVAILABLE = False
from datetime import datetime, timedelta
import warnings
import os
import time
import random
import json

warnings.filterwarnings("ignore")

# ── Gelişmiş ML Kütüphaneleri (opsiyonel — yoksa rule-based fallback) ──
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.calibration import CalibratedClassifierCV
    import xgboost as xgb
    import lightgbm as lgb
    from catboost import CatBoostClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────
# SAYFA AYARI
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BİST Ultimate Quant Terminal v1.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────
# KURUMSAL CSS — IBM Plex + JetBrains Mono hybrid
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #060A10 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    color: #C9D1D9;
}
[data-testid="stSidebar"] {
    background: #090D14 !important;
    border-right: 1px solid #161B22 !important;
}

/* ── HEADER ── */
.uq-header {
    background: linear-gradient(135deg, #0A1628 0%, #0D2040 50%, #0A1628 100%);
    border: 1px solid #1E3A5F;
    border-radius: 14px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.uq-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #1A56DB, #06B6D4, #10B981, #F59E0B, #1A56DB);
    background-size: 300% 100%;
    animation: hdrShift 6s linear infinite;
}
@keyframes hdrShift { 0%{background-position:0%} 100%{background-position:300%} }
.uq-header h1 {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 20px !important; font-weight: 700 !important;
    color: #E8F0FE !important; margin: 0 0 4px 0 !important;
}
.uq-header .sub { color: #4B7EB8; font-size: 12px; font-family: 'IBM Plex Mono', monospace; }
.uq-header .badges { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
.badge {
    background: rgba(26,86,219,0.12); border: 1px solid rgba(26,86,219,0.3);
    border-radius: 20px; padding: 3px 10px; font-size: 11px; color: #60A5FA;
    font-family: 'IBM Plex Mono', monospace;
}
.badge.g { background: rgba(16,185,129,0.10); border-color: rgba(16,185,129,0.28); color: #34D399; }
.badge.y { background: rgba(245,158,11,0.10); border-color: rgba(245,158,11,0.28); color: #FBBF24; }
.badge.p { background: rgba(168,85,247,0.10); border-color: rgba(168,85,247,0.28); color: #C084FC; }

/* ── TOOLTIP ── */
.tip-wrap { position: relative; display: inline-flex; align-items: center; gap: 6px; cursor: help; }
.tip-icon {
    display: inline-flex; align-items: center; justify-content: center;
    width: 16px; height: 16px; border-radius: 50%;
    background: rgba(96,165,250,0.15); border: 1px solid rgba(96,165,250,0.35);
    color: #60A5FA; font-size: 10px; font-weight: 700; cursor: help; flex-shrink: 0;
}
.tip-box {
    visibility: hidden; opacity: 0; position: absolute; z-index: 9999;
    bottom: calc(100% + 10px); left: 50%; transform: translateX(-50%);
    background: #0F1F35; border: 1px solid #1E3A5F; border-radius: 10px;
    padding: 12px 16px; width: 290px; font-size: 12px; color: #B0C8E8;
    line-height: 1.6; transition: opacity 0.2s ease, visibility 0.2s ease;
    box-shadow: 0 8px 32px rgba(0,0,0,0.6); pointer-events: none;
    font-family: 'IBM Plex Sans', sans-serif;
}
.tip-box::after {
    content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%);
    border: 6px solid transparent; border-top-color: #1E3A5F;
}
.tip-wrap:hover .tip-box { visibility: visible; opacity: 1; }
.tip-title { color: #60A5FA; font-weight: 600; font-size: 12px; margin-bottom: 4px; }

/* ── TABS ── */
[data-testid="stTabs"] button {
    font-family: 'IBM Plex Sans', sans-serif !important; font-size: 13px !important;
    font-weight: 500 !important; color: #6B8FAE !important; padding: 10px 18px !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #60A5FA !important; border-bottom: 2px solid #1A56DB !important;
}

/* ── METRIC KARTLARI ── */
[data-testid="stMetric"] {
    background: #0C1725 !important; border: 1px solid #161B22 !important;
    border-radius: 10px !important; padding: 12px 16px !important;
}
[data-testid="stMetricLabel"] { color: #6B8FAE !important; font-size: 12px !important; }
[data-testid="stMetricValue"] {
    color: #E2EBF6 !important; font-size: 19px !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── MASTER SCORE BADGE ── */
.mscore-badge {
    display: inline-block; padding: 4px 14px; border-radius: 20px;
    font-family: 'IBM Plex Mono', monospace; font-size: 13px; font-weight: 700;
}
.mscore-bull   { background: rgba(16,185,129,0.18); border: 1px solid #10B981; color: #34D399; }
.mscore-buy    { background: rgba(26,86,219,0.18);  border: 1px solid #1A56DB; color: #60A5FA; }
.mscore-hold   { background: rgba(107,143,174,0.18);border: 1px solid #6B8FAE; color: #94A3B8; }
.mscore-sell   { background: rgba(239,68,68,0.14);  border: 1px solid #EF4444; color: #FCA5A5; }
.mscore-danger { background: rgba(239,68,68,0.22);  border: 1px solid #DC2626; color: #F87171; }

/* ── SECTION TITLE ── */
.sec-title {
    font-size: 17px; font-weight: 600; color: #C5D8EE;
    border-left: 3px solid #1A56DB; padding-left: 12px; margin: 22px 0 12px 0;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: #0A1525 !important; border: 1px solid #161B22 !important;
    border-radius: 10px !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] * { color: #8AABCC !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #C5D8EE !important; }

/* ── AI KART ── */
.ai-card {
    background: linear-gradient(145deg, #0C1A2E, #0A1220);
    border: 1px solid #1C2840; border-radius: 12px; padding: 18px;
    margin-bottom: 12px; transition: border-color .2s, transform .2s;
}
.ai-card:hover { border-color: #1A56DB; transform: translateY(-2px); }
.ai-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.ai-sym { font-family: 'IBM Plex Mono', monospace; font-size: 18px; font-weight: 700; color: #E2EBF6; }
.ai-score-bar { height: 6px; border-radius: 3px; background: #161B22; margin: 8px 0; }
.ai-score-fill { height: 6px; border-radius: 3px; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #060A10; }
::-webkit-scrollbar-thumb { background: #161B22; border-radius: 3px; }

/* ── WARNING BOX ── */
.warn-box {
    background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.22);
    border-radius: 10px; padding: 12px 16px; color: #D4A017; font-size: 13px; margin-top: 16px;
}

/* ── STAT ROW ── */
.stat-row { display: flex; gap: 14px; margin: 18px 0; flex-wrap: wrap; }
.stat-box {
    flex: 1 1 150px; text-align: center; background: #0C1725;
    border: 1px solid #161B22; border-radius: 10px; padding: 16px;
}
.stat-num { font-family: 'IBM Plex Mono', monospace; font-size: 26px; font-weight: 700; color: #60A5FA; }
.stat-lbl { color: #6B8FAE; font-size: 12px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# YARDIMCI FONKSIYONLAR
# ─────────────────────────────────────────────────────────────────────
def tip(label, title, aciklama):
    return (f"<span class='tip-wrap'>{label}<span class='tip-icon'>?</span>"
            f"<span class='tip-box'><div class='tip-title'>{title}</div>{aciklama}</span></span>")


def show_table(df, score_col=None):
    if df is None or df.empty:
        st.info("Veri yok.")
        return
    STYLE = ("background:#0D1117;color:#C9D1D9;border-collapse:collapse;"
             "width:100%;font-size:13px;font-family:'IBM Plex Mono',monospace")
    TH = "background:#161B22;color:#58A6FF;padding:6px 10px;border:1px solid #30363D;text-align:center"
    TD = "padding:5px 10px;border:1px solid #21262D;text-align:center"
    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for col in df.columns:
            val = row[col]
            if col == score_col and isinstance(val, (int, float)):
                pct = max(0, min(100, int(val)))
                color = "#238636" if pct >= 60 else ("#E3B341" if pct >= 45 else "#DA3633")
                bar = (f"<div style='background:#21262D;border-radius:4px;height:13px;width:100%'>"
                       f"<div style='background:{color};width:{pct}%;height:13px;border-radius:4px'></div></div>"
                       f"<span style='font-size:11px'>{pct} Pts</span>")
                cells += f"<td style='{TD}'>{bar}</td>"
            else:
                sv = str(val)
                color = ""
                if col in ("Sinyal", "Karar", "AI Sinyali"):
                    color = ("#238636" if "AL" in sv and "SAT" not in sv
                             else "#DA3633" if "SAT" in sv else "#8B949E")
                elif col in ("BT Return (%)", "Sektör Momentumu (%)", "Kâr/Zarar (%)",
                             "Kar/Zarar TL", "Getiri (%)") and isinstance(val, (int, float)):
                    color = "#238636" if val >= 0 else "#DA3633"
                style = f"{TD};color:{color}" if color else TD
                cells += f"<td style='{style}'>{sv}</td>"
        rows_html += f"<tr>{cells}</tr>"
    header = "".join(f"<th style='{TH}'>{c}</th>" for c in df.columns)
    html = (f"<div style='overflow-x:auto'>"
            f"<table style='{STYLE}'><thead><tr>{header}</tr></thead>"
            f"<tbody>{rows_html}</tbody></table></div>")
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# AYARLAR & KONFİGÜRASYON
# ─────────────────────────────────────────────────────────────────────
CACHE_DIR           = os.path.join(os.environ.get("HOME", "/tmp"), "bist_cache")
CACHE_STALE_SECONDS = 3600
PORTFOLIO_FILE      = os.path.join(CACHE_DIR, "portfolio.json")
os.makedirs(CACHE_DIR, exist_ok=True)

# v23'teki 22 hisse + rbta10'daki BIST100 tam listesi birleştirildi
SECTOR_MAP = {
    # HAVACILIK
    "THYAO.IS": "HAVACILIK",    "PGSUS.IS": "HAVACILIK",
    # BANKACILIK
    "AKBNK.IS": "BANKACILIK",   "GARAN.IS": "BANKACILIK",
    "ISCTR.IS": "BANKACILIK",   "YKBNK.IS": "BANKACILIK",
    "HALKB.IS": "BANKACILIK",   "VAKBN.IS": "BANKACILIK",
    "TSKB.IS":  "BANKACILIK",   "QNBFB.IS": "BANKACILIK",
    # DEMİR-ÇELİK
    "EREGL.IS": "DEMİR-ÇELİK", "KRDMD.IS": "DEMİR-ÇELİK",
    "ISDMR.IS": "DEMİR-ÇELİK",
    # ENERJİ
    "TUPRS.IS": "ENERJİ",       "AKSEN.IS": "ENERJİ",
    "ZOREN.IS": "ENERJİ",       "ODAS.IS":  "ENERJİ",
    "ASTOR.IS": "ENERJİ",
    # KİMYA
    "PETKM.IS": "KİMYA",        "GUBRF.IS": "KİMYA",
    "SODA.IS":  "KİMYA",        "ALKIM.IS": "KİMYA",
    # HOLDİNG
    "KCHOL.IS": "HOLDİNG",      "SAHOL.IS": "HOLDİNG",
    "DOHOL.IS": "HOLDİNG",      "SISE.IS":  "HOLDİNG",
    "AGHOL.IS": "HOLDİNG",
    # PERAKENDE
    "BIMAS.IS": "PERAKENDE",    "MGROS.IS": "PERAKENDE",
    "SOKM.IS":  "PERAKENDE",
    # SAVUNMA
    "ASELS.IS": "SAVUNMA",      "HATEK.IS": "SAVUNMA",
    # TELEKOMÜNİKASYON
    "TCELL.IS": "TELEKOM",      "TTKOM.IS": "TELEKOM",
    # OTOMOTİV
    "FROTO.IS": "OTOMOTİV",     "TOASO.IS": "OTOMOTİV",
    "TTRAK.IS": "OTOMOTİV",     "OTKAR.IS": "OTOMOTİV",
    "BRISA.IS": "OTOMOTİV",
    # GAYRİMENKUL
    "EMLAK.IS": "GAYRİMENKUL",  "ISGYO.IS": "GAYRİMENKUL",
    "EKGYO.IS": "GAYRİMENKUL",
    # SİGORTA
    "ANHYT.IS": "SİGORTA",      "ANSGR.IS": "SİGORTA",
    "AGESA.IS": "SİGORTA",
    # TEKNOLOJİ
    "LOGO.IS":  "TEKNOLOJİ",    "NETAS.IS": "TEKNOLOJİ",
    # GIDA
    "ULKER.IS": "GIDA",         "TATGD.IS": "GIDA",
    "CCOLA.IS": "GIDA",         "AEFES.IS": "GIDA",
    # MADENCİLİK
    "KOZAL.IS": "MADENCİLİK",   "KOZAA.IS": "MADENCİLİK",
    # EV ALETLERİ
    "ARCLK.IS": "EV ALETLERİ",  "VESTL.IS": "EV ALETLERİ",
    "VESBE.IS": "EV ALETLERİ",
    # ÇİMENTO
    "AKCNS.IS": "ÇİMENTO",      "CIMSA.IS": "ÇİMENTO",
    "BOLUC.IS": "ÇİMENTO",
    # MADEN
    "ENKAI.IS": "İNŞAAT",
    # TEKSTİL
    "MAVI.IS":  "TEKSTİL",
}

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finance.yahoo.com/",
}

RANGE_MAP    = {"1y": "1y", "2y": "2y", "3m": "3m", "6m": "6m", "1mo": "1mo", "60d": "60d"}
INTERVAL_MAP = {"1d": "1d", "1h": "1h", "1wk": "1wk"}


# ─────────────────────────────────────────────────────────────────────
# KATMAN 1: VERİ ÇEKME MOTORU (curl_cffi — ban-proof)
# ─────────────────────────────────────────────────────────────────────
def fetch_yahoo_chart(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Yahoo Finance Chart API — curl_cffi ile doğrudan bağlantı."""
    if not symbol.endswith(".IS") and not symbol.endswith("=X"):
        symbol = f"{symbol}.IS"
    y_range    = RANGE_MAP.get(period, "1y")
    y_interval = INTERVAL_MAP.get(interval, "1d")
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?range={y_range}&interval={y_interval}")
    time.sleep(random.uniform(0.15, 0.5))
    try:
        kwargs = {"headers": HEADERS, "timeout": 14}
        if CURL_CFFI_AVAILABLE:
            kwargs["impersonate"] = "chrome"
        resp = cffi_requests.get(url, **kwargs)
        if resp.status_code != 200: return pd.DataFrame()
        data   = resp.json()
        result = data.get("chart", {}).get("result", [])
        if not result or result[0] is None: return pd.DataFrame()
        chart      = result[0]
        timestamps = chart.get("timestamp", [])
        if not timestamps: return pd.DataFrame()
        quote    = chart.get("indicators", {}).get("quote", [{}])[0]
        adjclose = (chart.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", []))
        df = pd.DataFrame({
            "Open":   quote.get("open",   [None] * len(timestamps)),
            "High":   quote.get("high",   [None] * len(timestamps)),
            "Low":    quote.get("low",    [None] * len(timestamps)),
            "Close":  adjclose if adjclose else quote.get("close", [None] * len(timestamps)),
            "Volume": quote.get("volume", [None] * len(timestamps)),
        })
        df.index      = [datetime.fromtimestamp(ts) for ts in timestamps]
        df.index.name = "Date"
        df.dropna(subset=["Close"], inplace=True)
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()


def _cache_path(sym, period, interval):
    return os.path.join(CACHE_DIR, f"{sym.replace('.IS','').replace('=X','usd').lower()}_{period}_{interval}.json")


def fetch_market_data(sym: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Cache-destekli veri çekici."""
    path = _cache_path(sym, period, interval)
    now  = time.time()
    if os.path.exists(path) and (now - os.path.getmtime(path)) < CACHE_STALE_SECONDS:
        try:
            with open(path, "r") as f:
                data = json.load(f)
            df = pd.DataFrame(data["data"], columns=data["columns"])
            df.index = pd.to_datetime(data["index"])
            df.index.name = "Date"
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            if not df.empty: return df
        except Exception:
            pass
    df = fetch_yahoo_chart(sym, period, interval)
    if not df.empty and len(df) >= 20:
        try:
            d = df.copy()
            d.index = d.index.astype(str)
            with open(path, "w") as f:
                json.dump({"data": d.values.tolist(),
                           "columns": list(d.columns),
                           "index": list(d.index)}, f)
        except Exception:
            pass
    elif os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            df = pd.DataFrame(data["data"], columns=data["columns"])
            df.index = pd.to_datetime(data["index"])
            df.index.name = "Date"
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        except Exception:
            pass
    return df


def _fetch_ticker_info(sym: str) -> dict:
    url = (f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{sym}"
           f"?modules=defaultKeyStatistics,summaryDetail")
    try:
        kwargs = {"headers": HEADERS, "timeout": 10}
        if CURL_CFFI_AVAILABLE:
            kwargs["impersonate"] = "chrome"
        resp = cffi_requests.get(url, **kwargs)
        if resp.status_code != 200: return {}
        data   = resp.json()
        result = data.get("quoteSummary", {}).get("result", [])
        if not result: return {}
        merged = {}
        for module in result[0].values():
            if isinstance(module, dict):
                merged.update(module)
        return {k: (v.get("raw") if isinstance(v, dict) else v) for k, v in merged.items()}
    except Exception:
        return {}


@st.cache_data(ttl=21600)
def fetch_fundamentals(sym: str) -> dict:
    info = _fetch_ticker_info(sym)
    return {
        "fk":   float(info.get("trailingPE") or info.get("forwardPE") or 10.0),
        "pddd": float(info.get("priceToBook") or 2.0),
        "beta": float(info.get("beta") or 1.0),
        "peg":  float(info.get("pegRatio") or 1.0),
        "roe":  float(info.get("returnOnEquity") or 0.15) * 100,
        "debt": float(info.get("debtToEquity") or 100.0),
    }


@st.cache_data(ttl=1800)
def fetch_news(sym=None, count=10) -> list:
    try:
        q   = sym if sym else "BIST borsa"
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={q}&newsCount={count}&quotesCount=0"
        kwargs = {"headers": HEADERS, "timeout": 10}
        if CURL_CFFI_AVAILABLE:
            kwargs["impersonate"] = "chrome"
        resp = cffi_requests.get(url, **kwargs)
        if resp.status_code != 200: return []
        news = resp.json().get("news", [])
        return [{
            "başlık": i.get("title", ""),
            "kaynak": i.get("publisher", ""),
            "tarih":  datetime.fromtimestamp(i.get("providerPublishTime", 0)).strftime("%d.%m.%Y %H:%M") if i.get("providerPublishTime") else "—",
            "link":   i.get("link", ""),
            "özet":   i.get("summary", ""),
        } for i in news]
    except Exception:
        return []


def market_status():
    now_tr  = datetime.utcnow() + timedelta(hours=3)
    weekday = now_tr.weekday()
    t       = now_tr.hour * 60 + now_tr.minute
    if weekday >= 5:
        return "🔴 KAPALI", "Hafta sonu", now_tr.strftime("%H:%M")
    if 9 * 60 + 30 <= t < 18 * 60:
        return "🟢 AÇIK", "Seans devam ediyor", now_tr.strftime("%H:%M")
    if t < 9 * 60 + 30:
        return "🟡 AÇILIŞA", f"{9*60+30-t} dk kaldı", now_tr.strftime("%H:%M")
    return "🔴 KAPALI", "Seans kapandı", now_tr.strftime("%H:%M")


# ─────────────────────────────────────────────────────────────────────
# KATMAN 2: İNDİKATÖR FABRİKASI (v23 tam set + rbta10 eklentileri)
# ─────────────────────────────────────────────────────────────────────
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # EMA'lar
    df["EMA9"]  = df["Close"].ewm(span=9,  adjust=False).mean()
    df["EMA21"] = df["Close"].ewm(span=21, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["MA5"]   = df["Close"].rolling(5).mean()
    df["MA22"]  = df["Close"].rolling(22).mean()
    # RSI
    delta = df["Close"].diff()
    gain  = delta.where(delta > 0, 0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + gain / (loss + 1e-9) + 1e-9))
    # Fisher RSI (rbta10'dan)
    rsi_s = (0.1 * (df["RSI"] - 50)).clip(-0.999, 0.999)
    df["Fisher_RSI"] = 0.5 * np.log((1 + rsi_s) / (1 - rsi_s + 1e-9))
    # MACD
    e12 = df["Close"].ewm(span=12, adjust=False).mean()
    e26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"]        = e12 - e26
    df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"]   = df["MACD"] - df["Signal_Line"]
    # Bollinger Bands
    df["BB_Middle"] = df["Close"].rolling(20).mean()
    std = df["Close"].rolling(20).std()
    df["BB_Upper"]  = df["BB_Middle"] + 2 * std
    df["BB_Lower"]  = df["BB_Middle"] - 2 * std
    df["BB_BW"]     = (df["BB_Upper"] - df["BB_Lower"]) / (df["BB_Middle"] + 1e-9)
    # ATR
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift()).abs(),
        (df["Low"]  - df["Close"].shift()).abs(),
    ], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()
    # Keltner Channels + Squeeze (rbta10'dan)
    df["KC_Upper"] = df["BB_Middle"] + 1.5 * df["ATR"]
    df["KC_Lower"] = df["BB_Middle"] - 1.5 * df["ATR"]
    df["Squeeze"]  = ((df["BB_Upper"] < df["KC_Upper"]) &
                      (df["BB_Lower"] > df["KC_Lower"])).astype(int)
    # Stochastic
    l14 = df["Low"].rolling(14).min()
    h14 = df["High"].rolling(14).max()
    df["Stoch_K"] = 100 * (df["Close"] - l14) / (h14 - l14 + 1e-9)
    df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()
    # OBV + türevleri (rbta10'dan)
    obv = [0]
    for i in range(1, len(df)):
        if df["Close"].iloc[i] > df["Close"].iloc[i-1]:
            obv.append(obv[-1] + df["Volume"].iloc[i])
        elif df["Close"].iloc[i] < df["Close"].iloc[i-1]:
            obv.append(obv[-1] - df["Volume"].iloc[i])
        else:
            obv.append(obv[-1])
    df["OBV"]          = obv
    df["OBV_Slope"]    = df["OBV"].diff(5) / (df["OBV"].rolling(5).std() + 1e-9)
    df["OBV_MA20"]     = df["OBV"].rolling(20).mean()
    df["OBV_Breakout"] = (df["OBV"] > df["OBV_MA20"]).astype(int)
    # Volume anomaly
    df["Vol_MA20"]   = df["Volume"].rolling(20).mean()
    df["Vol_Anomaly"] = df["Volume"] / (df["Vol_MA20"] + 1e-9)
    df["Vol_Spike"]  = (df["Vol_Anomaly"] >= 1.5).astype(int)
    # Smart Money Flow (rbta10'dan)
    clv = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / ((df["High"] - df["Low"]) + 1e-9)
    df["Smart_Money"] = np.where((df["Vol_Anomaly"] > 1.2) & (clv > 0.2), 1,
                        np.where((df["Vol_Anomaly"] > 1.2) & (clv < -0.2), -1, 0))
    # MFI proxy
    tp  = (df["High"] + df["Low"] + df["Close"]) / 3.0
    rmf = tp * df["Volume"]
    pdir = np.where(tp > tp.shift(1), 1, -1)
    pos_f = pd.Series(np.where(pdir == 1, rmf, 0), index=df.index).rolling(14).sum()
    neg_f = pd.Series(np.where(pdir == -1, rmf, 0), index=df.index).rolling(14).sum()
    df["MFI"] = 100 - (100 / (1 + pos_f / (neg_f + 1e-9)))
    # Log return volatility
    df["LogRetVol"] = np.log(df["Close"] / df["Close"].shift(1)).rolling(10).std()
    return df


# ─────────────────────────────────────────────────────────────────────
# KATMAN 3: PİYASA REJİMİ (iki kodun hybrid versiyonu)
# ─────────────────────────────────────────────────────────────────────
def detect_regime_hisse(df: pd.DataFrame) -> str:
    """Hisse bazlı rejim — ATR ve EMA'ya dayanır (v23 motoru)."""
    if len(df) < 20: return "SIDEWAYS"
    c       = df.iloc[-1]
    atr_s   = df["ATR"].tail(30)
    atr_pct = (c["ATR"] - atr_s.min()) / (atr_s.max() - atr_s.min() + 1e-9) * 100
    slope   = ((df["EMA21"].tail(5).iloc[-1] - df["EMA21"].tail(5).iloc[0])
               / (df["EMA21"].tail(5).iloc[0] + 1e-9) * 100)
    pos     = ((c["Close"] - df["Low"].tail(10).min())
               / (df["High"].tail(10).max() - df["Low"].tail(10).min() + 1e-9) * 100)
    if   pos < 15 and atr_pct > 75 and slope < -0.5: return "PANIC"
    elif atr_pct > 80:                                return "HIGH_VOL"
    elif abs(slope) > 0.2:                            return "TRENDING"
    return "SIDEWAYS"


def detect_regime_index(df_xu100: pd.DataFrame) -> tuple:
    """XU100 bazlı piyasa rejimi — rbta10 motoru."""
    if df_xu100.empty or len(df_xu100) < 22:
        return "VOLATILE (SİBER YEDEK MOD)", 0.7, 10000.0
    close = df_xu100["Close"]
    ma5   = close.rolling(5).mean().iloc[-1]
    ma22  = close.rolling(22).mean().iloc[-1]
    cur   = close.iloc[-1]
    vol22 = close.pct_change().rolling(22).std().iloc[-1] * np.sqrt(252)
    if cur < ma22 and ma5 < ma22:
        return "PANIC (SİBER DEFANS)", 0.4, cur
    elif cur > ma22 and ma5 > ma22:
        if vol22 > 0.25:
            return "VOLATILE (TEMKİNLİ BOĞA)", 0.85, cur
        return "BULLISH (GÜVENLİ BÖLGE)", 1.0, cur
    return "VOLATILE (TEMKİNLİ MOD)", 0.7, cur


# ─────────────────────────────────────────────────────────────────────
# KATMAN 4: ENSEMBLE AI SİNYAL MOTORU (rbta10 — sklearn optional)
# ─────────────────────────────────────────────────────────────────────
FEATURE_COLS = [
    "RSI", "Fisher_RSI", "MACD_Hist", "BB_BW", "Squeeze",
    "Stoch_K", "Stoch_D", "OBV_Slope", "OBV_Breakout",
    "Vol_Anomaly", "Vol_Spike", "Smart_Money", "MFI", "LogRetVol",
    "ATR",
]

def build_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    5 günlük +%5 geriye dönük momentum etiketi — LOOK-AHEAD BIAS YOK.

    Eski yöntem (shift(-5)) gelecek fiyatı kullanıyordu → veri sızıntısı.
    Yeni yöntem: t anında t-5..t aralığındaki geçmiş maksimum kâr fırsatını
    etiket olarak kullanır.  Model yalnızca t anında mevcut olan bilgiyle
    eğitilir; gelecek fiyat hiçbir şekilde feature veya label hesabına girmez.
    """
    df = df.copy()
    # Geçmiş 5 günlük penceredeki maksimum kapanış (t dahil, t-4..t)
    past_max = df["Close"].rolling(5).max()
    # 5 gün önce kapanış fiyatına göre o pencerede %5 kâr yakalandı mı?
    df["TARGET"] = (past_max >= df["Close"].shift(4) * 1.05).astype(int)
    # İlk 4 satır NaN olur (rolling penceresi dolmadan), temizle
    return df.dropna(subset=["TARGET"])


def train_ensemble(df: pd.DataFrame):
    """
    XGB + LGBM + CatBoost + RF ensemble eğit.

    OVERFİTTİNG DÜZELTMELERİ:
    1. Walk-forward split: eğitim penceresi zaman sırasına göre ayrılır,
       test kümesi eğitim setinin SONRASINDAKI verilerden oluşur.
    2. Erken durdurma (early stopping) XGB ve LGBM'de aktif → validation
       setine göre durur, ezberleme önlenir.
    3. Regularizasyon parametreleri güçlendirildi (reg_alpha, reg_lambda,
       min_child_samples, subsample, colsample_bytree).
    4. Modeller yalnızca tek hisseden değil, dışarıdan geçilen birleşik
       DataFrame üzerinde eğitilir (çoklu hisse havuzu için bkz. ana döngü).
    """
    if not SKLEARN_AVAILABLE or len(df) < 120:
        return None

    X = df[FEATURE_COLS].copy().fillna(0)
    y = df["TARGET"]

    # Walk-forward split: ilk %70 eğitim, sonraki %15 validation, son %15 test
    n     = len(df)
    tr_end = int(n * 0.70)
    va_end = int(n * 0.85)

    X_tr, y_tr = X.iloc[:tr_end],       y.iloc[:tr_end]
    X_va, y_va = X.iloc[tr_end:va_end], y.iloc[tr_end:va_end]

    if len(X_tr) < 60 or len(X_va) < 15:
        return None

    models = {}

    # ── XGBoost ──
    try:
        xg = xgb.XGBClassifier(
            n_estimators=100, max_depth=3, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.7,
            reg_alpha=0.5, reg_lambda=2.0,
            eval_metric="logloss",
            early_stopping_rounds=15, verbosity=0, n_jobs=1,
        )
        xg.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], verbose=False)
        models["xgb"] = xg
    except Exception:
        pass

    # ── LightGBM ──
    try:
        lg = lgb.LGBMClassifier(
            n_estimators=100, max_depth=3, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.7,
            min_child_samples=20, reg_alpha=0.5, reg_lambda=2.0,
            verbosity=-1, n_jobs=1,
        )
        lg.fit(X_tr, y_tr,
               eval_set=[(X_va, y_va)],
               callbacks=[lgb.early_stopping(15, verbose=False),
                          lgb.log_evaluation(-1)])
        models["lgbm"] = lg
    except Exception:
        pass

    # ── CatBoost ──
    try:
        cat = CatBoostClassifier(
            iterations=100, depth=3, learning_rate=0.05,
            l2_leaf_reg=4.0, early_stopping_rounds=15,
            eval_set=(X_va, y_va), verbose=False,
        )
        cat.fit(X_tr, y_tr)
        models["cat"] = cat
    except Exception:
        pass

    # ── Random Forest (calibrate edilmiş) ──
    try:
        rf_base = RandomForestClassifier(
            n_estimators=100, max_depth=4, min_samples_leaf=10,
            max_features=0.6, n_jobs=1, random_state=42,
        )
        rf = CalibratedClassifierCV(rf_base, cv=3, method="isotonic")
        rf.fit(X_tr, y_tr)
        models["rf"] = rf
    except Exception:
        pass

    return models if models else None


def ensemble_predict(models: dict, row: pd.Series) -> float:
    """Ensemble olasılık ortalaması (0-1)."""
    if not models:
        return 0.5
    X = row[FEATURE_COLS].fillna(0).values.reshape(1, -1)
    probs = []
    for m in models.values():
        try:
            probs.append(float(m.predict_proba(X)[0][1]))
        except Exception:
            pass
    return float(np.mean(probs)) if probs else 0.5


# ─────────────────────────────────────────────────────────────────────
# KATMAN 5: KELLY + ATR POZİSYON BOYUTLANDIRMASI (rbta10'dan)
# ─────────────────────────────────────────────────────────────────────
def kelly_position(prob: float, win_mult: float = 1.5, lose_mult: float = 1.0,
                   max_fraction: float = 0.25) -> float:
    """Kelly kriteriyyle optimal pozisyon oranı."""
    q = 1 - prob
    k = (prob * win_mult - q * lose_mult) / (win_mult + 1e-9)
    return float(max(0.0, min(max_fraction, k)))


def atr_position(capital: float, entry: float, atr: float,
                 risk_pct: float = 0.01) -> float:
    """ATR risk bazlı pozisyon miktarı (lot)."""
    risk_tl = capital * risk_pct
    stop    = 2.0 * atr
    return risk_tl / (stop + 1e-9)


# ─────────────────────────────────────────────────────────────────────
# KATMAN 6: MASTER_SCORE — AI + Teknik + Temel + Akıllı Para
# ─────────────────────────────────────────────────────────────────────
def calculate_master_score(df: pd.DataFrame, ai_prob: float,
                            index_trend: str, regime: str,
                            fund: dict) -> dict:
    """
    MASTER_SCORE = AI skoru (30%) + Teknik skor (35%)
                 + Temel skor (15%) + Akıllı Para skoru (20%)
    """
    if len(df) < 5:
        return {"master": 50, "signal": "TUT", "ai": 50, "tech": 50, "fund_s": 50, "smart": 50}
    c  = df.iloc[-1]
    p  = df.iloc[-2]

    # ── AI skoru ──
    ai_s = int(ai_prob * 100)

    # ── Teknik skor ──
    W = {
        "TRENDING": {"t": .50, "o": .20, "v": .20, "i": .10},
        "SIDEWAYS": {"t": .15, "o": .60, "v": .15, "i": .10},
        "HIGH_VOL": {"t": .30, "o": .30, "v": .30, "i": .10},
        "PANIC":    {"t": .10, "o": .10, "v": .60, "i": .20},
    }
    w   = W.get(regime, W["SIDEWAYS"])
    ts  = (50 + (25 if c["EMA9"]  > c["EMA21"] else -25)
              + (25 if c["EMA21"] > c["EMA50"] else -25)
              + (25 if c["MACD"]  > c["Signal_Line"] else -25))
    os_ = (50 + (25 if c["RSI"]     < 30 else (-25 if c["RSI"]     > 70 else 0))
              + (25 if c["Stoch_K"] < 20 else (-25 if c["Stoch_K"] > 80 else 0)))
    vs  = 50 + (30 if c["Close"] < c["BB_Lower"] else (-30 if c["Close"] > c["BB_Upper"] else 0))
    isc = 100 if index_trend == "POZİTİF" else 0
    tech_s = int(max(0, min(100, (max(0,min(100,ts))  * w["t"]
                                + max(0,min(100,os_)) * w["o"]
                                + max(0,min(100,vs))  * w["v"]
                                + isc                  * w["i"]))))

    # ── Temel skor ──
    fk_s   = 70 if fund["fk"]   < 10 else (50 if fund["fk"]   < 18 else 30)
    pddd_s = 70 if fund["pddd"] < 1.5 else (50 if fund["pddd"] < 3  else 30)
    roe_s  = 70 if fund["roe"]  > 20  else (50 if fund["roe"]  > 10 else 30)
    fund_s = int((fk_s + pddd_s + roe_s) / 3)

    # ── Akıllı Para skoru ──
    smart_s = 50
    smart_s += 20 if c.get("Smart_Money", 0) == 1 else (-20 if c.get("Smart_Money", 0) == -1 else 0)
    smart_s += 15 if c.get("OBV_Breakout", 0) == 1 else 0
    smart_s += 15 if c.get("Vol_Spike", 0) == 1 and c["Close"] > p["Close"] else 0
    smart_s += 10 if c.get("MFI", 50) < 25 else (-10 if c.get("MFI", 50) > 75 else 0)
    smart_s += 10 if c.get("Squeeze", 0) == 0 else -5  # squeeze çözüldüyse pozitif
    smart_s = max(0, min(100, int(smart_s)))

    # ── MASTER_SCORE ──
    master = int(ai_s * 0.30 + tech_s * 0.35 + fund_s * 0.15 + smart_s * 0.20)
    if regime == "PANIC":
        master = min(25, master)

    # ── Sinyal ──
    if   master >= 72: signal = "⚡ GÜÇLÜ AL"
    elif master >= 58: signal = "🟢 AL"
    elif master >= 46: signal = "🟡 TUT"
    elif master >= 32: signal = "🔴 SAT"
    else:              signal = "💀 GÜÇLÜ SAT"

    return {
        "master":  master, "signal": signal,
        "ai":      ai_s,   "tech":  tech_s,
        "fund_s":  fund_s, "smart": smart_s,
    }


# ─────────────────────────────────────────────────────────────────────
# KATMAN 7: ÇOKLU ZAMAN DİLİMİ REZONANS
# ─────────────────────────────────────────────────────────────────────
def calculate_mtf(sym: str) -> dict:
    w = fetch_market_data(sym, "2y",  "1wk")
    d = fetch_market_data(sym, "1y",  "1d")
    h = fetch_market_data(sym, "60d", "1h")
    def trend(df):
        return ("POZİTİF"
                if not df.empty and len(df) > 20
                and df["Close"].iloc[-1] > df["Close"].ewm(span=50).mean().iloc[-1]
                else "NEGATİF")
    tw, td, th = trend(w), trend(d), trend(h)
    pos = [tw, td, th].count("POZİTİF")
    M   = {3: (100, "TAM BOĞA"), 2: (66, "KISMİ BOĞA"),
           1: (33, "AYI EĞİLİM"), 0: (0, "TAM AYI")}
    sc, lbl = M.get(pos, (50, "NÖTR"))
    return {"alignment_score": sc, "alignment_lbl": lbl,
            "weekly": tw, "daily": td, "hourly": th}


# ─────────────────────────────────────────────────────────────────────
# KATMAN 8: BACKTEST MOTORU (v23 geliştirilmiş)
# ─────────────────────────────────────────────────────────────────────
def run_backtest(sym: str, df: pd.DataFrame,
                 capital: float = 100_000.0,
                 comm: float = 0.0005,
                 slip: float = 0.0005):
    """
    Backtest motoru — LOOK-AHEAD BIAS YOK.

    Eski versiyonda her çubukta tüm DataFrame'deki göstergeler (EMA50 vb.)
    zaten hesaplanmış halde geliyordu; bu göstergeler o çubuğun ÖTESİNDEKİ
    fiyatları da kullanarak hesaplanmıştı → geleceğe bakış.

    Düzeltme:
    • Göstergeler her i adımında YALNIZCA df.iloc[:i+1] alt kümesiyle
      hesaplanır (expanding window).  Bu, gerçek zamanlı uygulamayı taklit eder.
    • Signal sadece i anında mevcut olan bilgiye dayanır.
    • Pozisyon açma/kapama fiyatı bir sonraki çubuğun açılış fiyatıdır
      (gerçekçi uygulama — çubuğun kapanışında sinyal bilmek ama
      o fiyattan girmek mümkün değildir).
    """
    if df is None or len(df) < 40:
        return None

    bt     = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    cap    = capital
    pos    = 0
    ep     = sl = hp = ps = 0.0
    ed     = None
    trades = []
    eq     = [capital]

    for i in range(20, len(bt) - 1):   # -1: giriş/çıkış bir sonraki çubukta
        # ── SADECE geçmiş veriyi kullan (i+1 dahil değil) ──
        window = bt.iloc[:i + 1].copy()

        # Göstergeleri bu pencerede yeniden hesapla
        cl   = window["Close"]
        ema9  = cl.ewm(span=9,  adjust=False).mean().iloc[-1]
        ema21 = cl.ewm(span=21, adjust=False).mean().iloc[-1]
        ema50 = cl.ewm(span=50, adjust=False).mean().iloc[-1]

        delta = cl.diff()
        gain  = delta.where(delta > 0, 0).rolling(14).mean()
        loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi   = (100 - (100 / (1 + gain / (loss + 1e-9)))).iloc[-1]

        e12  = cl.ewm(span=12, adjust=False).mean()
        e26  = cl.ewm(span=26, adjust=False).mean()
        macd_hist = ((e12 - e26) - (e12 - e26).ewm(span=9, adjust=False).mean()).iloc[-1]

        tr_s = pd.concat([
            window["High"] - window["Low"],
            (window["High"] - window["Close"].shift()).abs(),
            (window["Low"]  - window["Close"].shift()).abs(),
        ], axis=1).max(axis=1)
        atr = tr_s.rolling(14).mean().iloc[-1]
        if np.isnan(atr) or atr <= 0:
            atr = window["Close"].iloc[-1] * 0.02

        cur_close = window["Close"].iloc[-1]

        # ── Basit kural tabanlı sinyal (i anındaki bilgiyle) ──
        ts  = 50 + (25 if ema9 > ema21 else -25) + (25 if macd_hist > 0 else -25)
        os_ = 50 + (25 if rsi < 30 else (-25 if rsi > 70 else 0))
        sc  = int(ts * 0.6 + os_ * 0.4)
        sig = "AL" if sc >= 60 else ("SAT" if sc <= 40 else "TUT")

        # ── Bir sonraki çubuğun fiyatlarıyla işlem yap ──
        next_row = bt.iloc[i + 1]
        cd       = bt.index[i + 1]
        exec_open = float(next_row["Open"])   # gerçekçi: signal sonraki açılışta uygulanır

        if pos == 1:
            if cur_close > hp:
                hp  = cur_close
                nsl = hp - 2.0 * atr
                if nsl > sl:
                    sl = nsl
            # Stop kontrol: sonraki çubuğun low'una göre
            if float(next_row["Low"]) <= sl or sig == "SAT":
                xp  = (sl if float(next_row["Low"]) <= sl else exec_open) * (1 - slip)
                fee = xp * ps * comm
                cap = ps * xp - fee
                trades.append({
                    "Hisse": sym, "Giriş": str(ed.date()), "Çıkış": str(cd.date()),
                    "Giriş (TL)": round(ep, 2), "Çıkış (TL)": round(xp, 2),
                    "Tip": "SL" if float(next_row["Low"]) <= sl else "SIG",
                    "Kâr/Zarar": round((xp - ep) * ps - fee, 2),
                    "Getiri (%)": round((xp - ep) / (ep + 1e-9) * 100, 2),
                })
                pos = ps = 0.0

        elif pos == 0 and sig == "AL":
            ep  = exec_open * (1 + slip)
            ed  = cd
            cap -= cap * comm
            ps  = cap / (ep + 1e-9)
            cap = 0.0
            pos = 1
            hp  = exec_open
            sl  = ep - 2.0 * atr

        eq.append(ps * cur_close if pos == 1 else cap)

    tdf  = pd.DataFrame(trades)
    eq_s = pd.Series(eq)
    mdd  = ((eq_s - eq_s.cummax()) / (eq_s.cummax() + 1e-9)).min() * 100
    wr   = (len(tdf[tdf["Kâr/Zarar"] > 0]) / len(tdf) * 100) if len(tdf) > 0 else 0.0
    return {
        "trades": tdf, "total_return": (eq_s.iloc[-1] - capital) / capital * 100,
        "max_drawdown": mdd, "win_rate": wr, "final_value": eq_s.iloc[-1],
        "equity_curve": eq_s.tolist(),
    }


# ─────────────────────────────────────────────────────────────────────
# KATMAN 9: ANA ANALİZ ORKESTRATÖRü
# ─────────────────────────────────────────────────────────────────────
def analyze(sym: str, raw_df: pd.DataFrame,
            models=None, xu100_df=None, usd_df=None,
            index_trend: str = "POZİTİF") -> dict | None:
    """Tek hisse için tam analiz paketi."""
    if raw_df is None or len(raw_df) < 40: return None
    df = raw_df.copy()
    df.columns = [str(c).strip().title() for c in df.columns]
    df = df[~df.index.duplicated(keep="last")]
    req = ["Open", "High", "Low", "Close", "Volume"]
    if any(c not in df.columns for c in req): return None
    df[req] = df[req].ffill().bfill()
    df      = df.dropna(subset=req)
    if len(df) < 40: return None

    df     = calculate_indicators(df)
    df     = build_target(df)
    df.dropna(subset=["EMA50", "RSI", "ATR", "MACD", "Signal_Line",
                       "BB_Upper", "BB_Lower", "Stoch_K"], inplace=True)
    if len(df) < 5: return None

    regime = detect_regime_hisse(df)
    cr     = df.iloc[-1]
    pr     = df.iloc[-2]

    # AI olasılığı
    if models and SKLEARN_AVAILABLE:
        ai_prob = ensemble_predict(models, cr)
    else:
        # Rule-based fallback (AI yokken basit heuristik)
        score_r = 0.5
        if cr.get("RSI", 50) < 35:       score_r += 0.15
        if cr.get("RSI", 50) > 65:       score_r -= 0.15
        if cr.get("MACD_Hist", 0) > 0:   score_r += 0.10
        if cr.get("OBV_Breakout", 0):     score_r += 0.10
        if cr.get("Smart_Money", 0) == 1: score_r += 0.10
        if cr.get("Squeeze", 0) == 1:     score_r -= 0.05
        ai_prob = max(0.05, min(0.95, score_r))

    fund  = fetch_fundamentals(sym)
    mtf   = calculate_mtf(sym)
    score = calculate_master_score(df, ai_prob, index_trend, regime, fund)

    # MTF uyumundan bonus/ceza
    if mtf["alignment_score"] == 100: score["master"] = min(100, score["master"] + 5)
    if mtf["alignment_score"] == 0:   score["master"] = max(0,   score["master"] - 10)

    # Kelly + ATR pozisyon boyutu (100k sermaye varsayımı)
    kelly_frac = kelly_position(ai_prob)
    atr_lot    = atr_position(100_000, float(cr["Close"]), float(cr["ATR"]))

    # Pivot
    pvt  = (cr["High"] + cr["Low"] + cr["Close"]) / 3
    tact = ("🚀 TREND TAKİBİ" if regime == "TRENDING" and score["master"] >= 58 else
            "🔄 RANGE TRADING" if regime == "SIDEWAYS" else
            "🛡️ SİBER DEFANS"  if regime == "PANIC"   else "👀 GÖZLEM")

    return {
        "sym":    sym,
        "price":  float(cr["Close"]),
        "chg":    float(df["Close"].pct_change().iloc[-1] * 100),
        "score":  score,  # dict: master, signal, ai, tech, fund_s, smart
        "regime": regime,
        "sektör": SECTOR_MAP.get(sym, "DİĞER"),
        "rsi":    float(cr["RSI"]),
        "macd":   float(cr["MACD_Hist"]),
        "atr":    float(cr["ATR"]),
        "stop":   float(cr["Close"] - 2 * cr["ATR"]),
        "pivot":  pvt,
        "r1": 2*pvt - cr["Low"],   "r2": pvt + (cr["High"] - cr["Low"]),
        "s1": 2*pvt - cr["High"],  "s2": pvt - (cr["High"] - cr["Low"]),
        "fund":       fund,
        "mtf":        mtf,
        "tactic":     tact,
        "ai_prob":    round(ai_prob * 100, 1),
        "kelly_frac": round(kelly_frac * 100, 1),
        "atr_lot":    round(atr_lot, 0),
        "df":         df,
        "squeeze":    int(cr.get("Squeeze", 0)),
        "smart_money": int(cr.get("Smart_Money", 0)),
        "obv_break":   int(cr.get("OBV_Breakout", 0)),
        "52w_high":   float(df["High"].tail(252).max()),
        "52w_low":    float(df["Low"].tail(252).min()),
    }


# ─────────────────────────────────────────────────────────────────────
# KATMAN 10: GRAFİK MOTORLARI
# ─────────────────────────────────────────────────────────────────────
def make_candle_chart(r: dict):
    df  = r["df"].tail(60)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05, row_width=[0.3, 0.7])
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Fiyat",
        increasing_line_color="#26a641", decreasing_line_color="#da3633"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA9"],
        line=dict(color="#79c0ff", width=1, dash="dot"), name="EMA9"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA21"],
        line=dict(color="#ff7b72", width=1.5), name="EMA21"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"],
        line=dict(color="#8b949e", width=1, dash="dash"), name="BB Üst", fill=None), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"],
        line=dict(color="#8b949e", width=1, dash="dash"), name="BB Alt",
        fill="tonexty", fillcolor="rgba(139,148,158,0.06)"), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"],
        marker_color=np.where(df["MACD_Hist"] > 0, "#238636", "#da3633"),
        name="MACD Hist"), row=2, col=1)
    fig.update_layout(template="plotly_dark", height=430,
                      margin=dict(l=10, r=10, t=10, b=10),
                      xaxis_rangeslider_visible=False)
    return fig


def make_advanced_chart(df, sym, indicators, bars=120):
    df = df.tail(bars).copy()
    n_rows = 1
    row_h  = [0.5]
    extra  = [i for i in ["RSI", "MACD", "Stochastic", "OBV", "MFI"] if i in indicators]
    for _ in extra:
        n_rows += 1; row_h.append(0.15)
    fig = make_subplots(rows=n_rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, row_heights=row_h)
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Fiyat",
        increasing_line_color="#26a641", decreasing_line_color="#da3633"), row=1, col=1)
    if "EMA9"   in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA9"],
            line=dict(color="#79c0ff", width=1, dash="dot"), name="EMA9"), row=1, col=1)
    if "EMA21"  in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA21"],
            line=dict(color="#ff7b72", width=1.5), name="EMA21"), row=1, col=1)
    if "EMA50"  in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"],
            line=dict(color="#f0883e", width=2), name="EMA50"), row=1, col=1)
    if "Bollinger" in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"],
            line=dict(color="#8b949e", width=1, dash="dash"), name="BB Üst", fill=None), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"],
            line=dict(color="#8b949e", width=1, dash="dash"), name="BB Alt",
            fill="tonexty", fillcolor="rgba(139,148,158,0.07)"), row=1, col=1)
    cur = 2
    for ind in extra:
        if ind == "RSI":
            fig.add_trace(go.Scatter(x=df.index, y=df["RSI"],
                line=dict(color="#e3b341", width=1.5), name="RSI"), row=cur, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#da3633", row=cur, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#238636", row=cur, col=1)
            fig.update_yaxes(title_text="RSI", row=cur, col=1, range=[0, 100])
        elif ind == "MACD":
            fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"],
                marker_color=np.where(df["MACD_Hist"] > 0, "#238636", "#da3633"),
                name="MACD Hist"), row=cur, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],
                line=dict(color="#58a6ff", width=1), name="MACD"), row=cur, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["Signal_Line"],
                line=dict(color="#ff7b72", width=1), name="Signal"), row=cur, col=1)
            fig.update_yaxes(title_text="MACD", row=cur, col=1)
        elif ind == "Stochastic":
            fig.add_trace(go.Scatter(x=df.index, y=df["Stoch_K"],
                line=dict(color="#d2a8ff", width=1.5), name="%K"), row=cur, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["Stoch_D"],
                line=dict(color="#ffa657", width=1), name="%D"), row=cur, col=1)
            fig.add_hline(y=80, line_dash="dash", line_color="#da3633", row=cur, col=1)
            fig.add_hline(y=20, line_dash="dash", line_color="#238636", row=cur, col=1)
            fig.update_yaxes(title_text="Stoch", row=cur, col=1, range=[0, 100])
        elif ind == "OBV":
            fig.add_trace(go.Scatter(x=df.index, y=df["OBV"],
                line=dict(color="#3fb950", width=1.5), name="OBV",
                fill="tozeroy", fillcolor="rgba(63,185,80,0.08)"), row=cur, col=1)
            fig.update_yaxes(title_text="OBV", row=cur, col=1)
        elif ind == "MFI":
            fig.add_trace(go.Scatter(x=df.index, y=df["MFI"],
                line=dict(color="#c084fc", width=1.5), name="MFI"), row=cur, col=1)
            fig.add_hline(y=80, line_dash="dash", line_color="#da3633", row=cur, col=1)
            fig.add_hline(y=20, line_dash="dash", line_color="#238636", row=cur, col=1)
            fig.update_yaxes(title_text="MFI", row=cur, col=1, range=[0, 100])
        cur += 1
    fig.update_layout(template="plotly_dark",
                      height=200 + n_rows * 160,
                      title=dict(text=f"⚡ {sym.replace('.IS','')} — Teknik Analiz",
                                 font=dict(color="#58a6ff", size=15)),
                      margin=dict(l=10, r=10, t=50, b=10),
                      xaxis_rangeslider_visible=False,
                      legend=dict(orientation="h", y=1.02, x=0))
    return fig


def make_equity_chart(eq, sym):
    s   = pd.Series(eq)
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=s.values, mode="lines",
        line=dict(color="#58a6ff", width=2),
        fill="tozeroy", fillcolor="rgba(88,166,255,0.08)", name="Portföy"))
    fig.add_hline(y=eq[0], line_dash="dash", line_color="#8b949e",
                  annotation_text="Başlangıç")
    fig.update_layout(template="plotly_dark", height=240,
                      title=dict(text=f"{sym.replace('.IS','')} — Equity Curve",
                                 font=dict(color="#58a6ff")),
                      margin=dict(l=10, r=10, t=40, b=10))
    return fig


def make_portfolio_pie(rows):
    fig = go.Figure(go.Pie(
        labels=[r["hisse"] for r in rows], values=[r["maliyet"] for r in rows],
        hole=0.45, textinfo="label+percent",
        marker=dict(colors=["#58a6ff","#238636","#f0883e","#d2a8ff",
                             "#ffa657","#79c0ff","#ff7b72","#e3b341"])))
    fig.update_layout(template="plotly_dark", height=300,
                      title=dict(text="Portföy Dağılımı (Maliyet)", font=dict(color="#58a6ff")),
                      margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
    return fig


# ─────────────────────────────────────────────────────────────────────
# KATMAN 11: UI RENDER FONKSİYONLARI
# ─────────────────────────────────────────────────────────────────────
def score_css(master: int) -> str:
    if master >= 72: return "mscore-bull"
    if master >= 58: return "mscore-buy"
    if master >= 46: return "mscore-hold"
    if master >= 32: return "mscore-sell"
    return "mscore-danger"


def render_hisse_kart(r: dict):
    sc   = r["score"]
    sym  = r["sym"].replace(".IS", "")
    css  = score_css(sc["master"])
    st.markdown(f"""
<div class='sec-title'>🎯 {sym} — Master Analiz Kartı</div>
""", unsafe_allow_html=True)

    # Master skor ana satırı
    col_s, col_ai, col_t, col_f, col_sm = st.columns(5)
    col_s.metric("⚡ MASTER SCORE", f"{sc['master']} / 100")
    col_ai.metric("🤖 AI Olasılık", f"%{r['ai_prob']}")
    col_t.metric("📊 Teknik Skor",  f"{sc['tech']} / 100")
    col_f.metric("📋 Temel Skor",   f"{sc['fund_s']} / 100")
    col_sm.metric("💰 Akıllı Para", f"{sc['smart']} / 100")

    # Sinyal badge
    st.markdown(f"""
<div style='text-align:center;margin:10px 0'>
  <span class='mscore-badge {css}' style='font-size:16px;padding:8px 28px'>{sc['signal']}</span>
</div>
""", unsafe_allow_html=True)

    # MTF + 52H
    mtf = r["mtf"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Trend Rezonansı", mtf["alignment_lbl"])
    c2.metric("Haftalık (W)",    mtf["weekly"])
    c3.metric("Günlük (D)",      mtf["daily"])
    c4.metric("Seanslık (H)",    mtf["hourly"])

    w1, w2, w3, w4 = st.columns(4)
    w1.metric("52H Yüksek", f"{r['52w_high']:.2f} TL")
    w2.metric("52H Düşük",  f"{r['52w_low']:.2f} TL")
    w3.metric("Zirveye Mesafe", f"%{(r['price']-r['52w_high'])/r['52w_high']*100:.1f}")
    w4.metric("Kelly Fraksiyon", f"%{r['kelly_frac']}")

    # Sinyaller satırı
    squeeze_ic  = "🟡 AKTİF" if r["squeeze"]    else "⚪ YOK"
    smart_ic    = "🟢 BİRİKİM" if r["smart_money"] == 1 else ("🔴 DAĞITIM" if r["smart_money"] == -1 else "⚪ NÖTR")
    obv_ic      = "🟢 YUKARI" if r["obv_break"] else "⚪ ALTTA"
    s1, s2, s3 = st.columns(3)
    s1.metric("Bollinger Sıkışma", squeeze_ic)
    s2.metric("Akıllı Para Akışı", smart_ic)
    s3.metric("OBV Kırılım",       obv_ic)

    # Ana grafik
    st.plotly_chart(make_candle_chart(r), use_container_width=True)

    # Pivot analizi
    with st.expander("📊 Pivot Seviyeleri (Destek / Direnç)", expanded=False):
        st.markdown(
            f"<table style='width:100%;text-align:center;color:white;background:#161B22'>"
            f"<tr><th>S2</th><th>S1</th><th>PİVOT</th><th>R1</th><th>R2</th></tr>"
            f"<tr><td style='color:#FF7B72'>{r['s2']:.2f}</td>"
            f"<td style='color:#FF7B72'>{r['s1']:.2f}</td>"
            f"<td><b>{r['pivot']:.2f}</b></td>"
            f"<td style='color:#58A6FF'>{r['r1']:.2f}</td>"
            f"<td style='color:#58A6FF'>{r['r2']:.2f}</td></tr></table>",
            unsafe_allow_html=True)

    # Risk yönetimi
    with st.expander("🛡️ Risk Yönetimi & Pozisyon Boyutlandırması", expanded=False):
        st.markdown(tip("**Risk Parametreleri**", "ATR Stop & Kelly",
            "ATR Stop: Kapanışın 2×ATR altı — bu kırılırsa pozisyon kapatılır. "
            "Kelly Fraksiyon: Optimal sermaye yüzdesi (AI olasılığına göre). "
            "ATR Lot: 100.000 TL sermayede %1 risk ile alabileceğiniz tahmini lot."),
            unsafe_allow_html=True)
        r1c, r2c, r3c, r4c = st.columns(4)
        r1c.metric("ATR Trailing Stop", f"{r['stop']:.2f} TL")
        r2c.metric("Kelly Sermaye (%)", f"%{r['kelly_frac']}")
        r3c.metric("ATR Lot (100k)", f"{r['atr_lot']:.0f} adet")
        r4c.metric("Beta", f"{r['fund']['beta']:.2f}")
        e1, e2, e3, e4 = st.columns(4)
        e1.metric("F/K", f"{r['fund']['fk']:.1f}")
        e2.metric("PD/DD", f"{r['fund']['pddd']:.2f}")
        e3.metric("ROE (%)", f"%{r['fund']['roe']:.1f}")
        e4.metric("Borç/Özkaynak", f"%{r['fund']['debt']:.0f}")

    # Backtest
    with st.expander("📈 Backtest Raporu (1Y, 100.000 TL başlangıç)", expanded=False):
        bt = run_backtest(r["sym"], r["df"])
        if bt:
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Net Getiri",    f"%{bt['total_return']:.2f}")
            b2.metric("Max Drawdown",  f"%{bt['max_drawdown']:.2f}")
            b3.metric("Win Rate",      f"%{bt['win_rate']:.1f}")
            b4.metric("Nihai Değer",   f"{bt['final_value']:,.0f} TL")
            st.plotly_chart(make_equity_chart(bt["equity_curve"], r["sym"]),
                            use_container_width=True)
            if not bt["trades"].empty:
                show_table(bt["trades"].tail(5).reset_index(drop=True))


def render_screener(results: list):
    st.markdown("<div class='sec-title'>🔍 MASTER SCORE Akıllı Tarayıcı</div>", unsafe_allow_html=True)
    cf1, cf2, cf3, cf4 = st.columns(4)
    with cf1:
        f_sig = st.multiselect("Sinyal", ["⚡ GÜÇLÜ AL","🟢 AL","🟡 TUT","🔴 SAT","💀 GÜÇLÜ SAT"],
                               default=["⚡ GÜÇLÜ AL","🟢 AL"])
    with cf2:
        f_reg = st.multiselect("Piyasa Rejimi",
                               ["TRENDING","SIDEWAYS","HIGH_VOL","PANIC"],
                               default=["TRENDING","SIDEWAYS","HIGH_VOL","PANIC"])
    with cf3:
        m_align = st.slider("Min Trend Uyumu (%)", 0, 100, 33, step=33)
    with cf4:
        min_ai = st.slider("Min AI Olasılık (%)", 0, 100, 40)
    rows = []
    for r in results:
        sc  = r["score"]
        bt  = run_backtest(r["sym"], r["df"])
        rows.append({
            "Hisse":          r["sym"].replace(".IS",""),
            "Sektör":         r["sektör"],
            "Master Skor":    sc["master"],
            "AI Sinyali":     sc["signal"],
            "AI (%)" :        r["ai_prob"],
            "Teknik":         sc["tech"],
            "Akıllı Para":    sc["smart"],
            "Rejim":          r["regime"],
            "Trend Uyumu":    r["mtf"]["alignment_score"],
            "BT Return (%)":  round(bt["total_return"], 2) if bt else 0.0,
            "MaxDD (%)":      round(bt["max_drawdown"],  2) if bt else 0.0,
        })
    df_s = pd.DataFrame(rows)
    if not df_s.empty:
        if f_sig:  df_s = df_s[df_s["AI Sinyali"].isin(f_sig)]
        if f_reg:  df_s = df_s[df_s["Rejim"].isin(f_reg)]
        df_s = df_s[df_s["Trend Uyumu"] >= m_align]
        df_s = df_s[df_s["AI (%)"]      >= min_ai]
        show_table(df_s.sort_values("Master Skor", ascending=False).reset_index(drop=True),
                   score_col="Master Skor")


def render_advanced_chart_tab(results: list):
    st.markdown("<div class='sec-title'>🕯️ Gelişmiş Grafik & Teknik Analiz Stüdyosu</div>",
                unsafe_allow_html=True)
    col_sym, col_period, col_bars = st.columns(3)
    with col_sym:
        sel = st.selectbox("Hisse", [r["sym"] for r in results],
                           format_func=lambda x: x.replace(".IS",""), key="adv_sym")
    with col_period:
        period = st.selectbox("Periyot", ["1y","6m","3m","2y"], key="adv_period")
    with col_bars:
        bars = st.slider("Bar Sayısı", 30, 365, 120, key="adv_bars")
    inds = st.multiselect("Göstergeler",
        ["EMA9","EMA21","EMA50","Bollinger","RSI","MACD","Stochastic","OBV","MFI"],
        default=["EMA21","EMA50","Bollinger","RSI","MACD","MFI"], key="adv_inds")
    r = next((x for x in results if x["sym"] == sel), None)
    if not r:
        st.warning("Hisse verisi bulunamadı.")
        return
    df_adv = fetch_market_data(sel, period, "1d")
    if df_adv.empty:
        st.warning("Veri çekilemedi.")
        return
    df_adv.columns = [str(c).strip().title() for c in df_adv.columns]
    df_adv = calculate_indicators(df_adv)
    st.plotly_chart(make_advanced_chart(df_adv, sel, inds, bars), use_container_width=True)
    # İstatistik özeti
    recent = df_adv.tail(bars)
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Ort. Günlük Getiri", f"%{recent['Close'].pct_change().mean()*100:.3f}")
    s2.metric("Volatilite",         f"%{recent['Close'].pct_change().std()*100:.2f}")
    s3.metric("Max Fiyat",          f"{recent['High'].max():.2f} TL")
    s4.metric("Min Fiyat",          f"{recent['Low'].min():.2f} TL")
    sharpe = (recent["Close"].pct_change().mean() /
              (recent["Close"].pct_change().std() + 1e-9) * (252**0.5))
    s5.metric("Sharpe (Ham)", f"{sharpe:.2f}")


def render_portfolio_tab(results: list):
    st.markdown("<div class='sec-title'>💼 Portföy Takip & Kar/Zarar Hesabı</div>",
                unsafe_allow_html=True)
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []
        if os.path.exists(PORTFOLIO_FILE):
            try:
                with open(PORTFOLIO_FILE, "r") as f:
                    st.session_state.portfolio = json.load(f)
            except Exception:
                pass
    portfolio = st.session_state.portfolio
    with st.expander("➕ Yeni Pozisyon Ekle", expanded=len(portfolio) == 0):
        all_syms = list(SECTOR_MAP.keys())
        pc1, pc2, pc3, pc4 = st.columns(4)
        with pc1: p_sym  = st.selectbox("Hisse", sorted(set(all_syms)), format_func=lambda x: x.replace(".IS",""), key="p_sym")
        with pc2: p_lot  = st.number_input("Adet", min_value=1, value=100, key="p_lot")
        with pc3: p_cost = st.number_input("Alış Fiyatı", min_value=0.01, value=10.0, format="%.2f", key="p_cost")
        with pc4: p_date = st.date_input("Alış Tarihi", key="p_date")
        if st.button("✅ Portföye Ekle"):
            portfolio.append({"hisse": p_sym, "lot": int(p_lot),
                              "maliyet": round(float(p_cost), 2), "tarih": str(p_date)})
            st.session_state.portfolio = portfolio
            try:
                with open(PORTFOLIO_FILE, "w") as f: json.dump(portfolio, f, ensure_ascii=False)
            except Exception: pass
            st.success(f"{p_sym.replace('.IS','')} eklendi!")
            st.rerun()
    if not portfolio:
        st.info("Henüz pozisyon yok. Yukarıdan ekleyin.")
        return
    rows = []
    tot_cost = tot_cur = 0.0
    for pos in portfolio:
        sym  = pos["hisse"]
        lot  = pos["lot"]
        cost = pos["maliyet"]
        df_c = fetch_market_data(sym, "5d", "1d")
        cur  = float(df_c["Close"].iloc[-1]) if not df_c.empty else cost
        t_c  = lot * cost
        t_v  = lot * cur
        tot_cost += t_c; tot_cur += t_v
        rows.append({"Hisse": sym.replace(".IS",""), "Lot": lot,
                     "Alış": f"{cost:.2f}", "Anlık": f"{cur:.2f}",
                     "Maliyet (TL)": round(t_c, 2), "Güncel (TL)": round(t_v, 2),
                     "Kar/Zarar TL": round(t_v - t_c, 2),
                     "Kâr/Zarar (%)": round((cur - cost) / cost * 100, 2),
                     "Sektör": SECTOR_MAP.get(sym, "DİĞER")})
    show_table(pd.DataFrame(rows))
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    pnl = tot_cur - tot_cost
    m1.metric("Toplam Maliyet", f"{tot_cost:,.0f} TL")
    m2.metric("Güncel Değer",   f"{tot_cur:,.0f} TL")
    m3.metric("Toplam K/Z",     f"{pnl:,.0f} TL", delta=f"%{pnl/tot_cost*100:.2f}")
    m4.metric("Pozisyon",       str(len(portfolio)))
    if len(rows) > 1:
        st.plotly_chart(make_portfolio_pie([{"hisse": r["Hisse"], "maliyet": r["Maliyet (TL)"]} for r in rows]),
                        use_container_width=True)
    with st.expander("🗑️ Pozisyon Sil"):
        opts = [f"{p['hisse'].replace('.IS','')} — {p['lot']} lot @ {p['maliyet']}" for p in portfolio]
        sel  = st.selectbox("Sil:", opts, key="del_sel")
        if st.button("❌ Sil"):
            portfolio.pop(opts.index(sel))
            st.session_state.portfolio = portfolio
            try:
                with open(PORTFOLIO_FILE, "w") as f: json.dump(portfolio, f, ensure_ascii=False)
            except Exception: pass
            st.success("Silindi.")
            st.rerun()


def render_news_tab(results: list):
    st.markdown("<div class='sec-title'>📰 Piyasa Haberleri & Gündem</div>", unsafe_allow_html=True)
    nc1, nc2 = st.columns([2, 1])
    with nc1:
        news_sym = st.selectbox("Hisse (boş = genel BIST)",
                                ["— Genel BIST"] + [r["sym"] for r in results],
                                format_func=lambda x: x.replace(".IS","") if x != "— Genel BIST" else x,
                                key="news_sym")
    with nc2:
        news_count = st.slider("Haber Sayısı", 5, 20, 10, key="nc")
    sym_q = None if news_sym == "— Genel BIST" else news_sym
    with st.spinner("Haberler yükleniyor..."):
        news = fetch_news(sym_q, news_count)
    if not news:
        st.warning("Haber çekilemedi.")
        return
    st.markdown(f"**{len(news)} haber bulundu** — {news_sym}")
    st.markdown("---")
    for item in news:
        col_i, col_l = st.columns([5, 1])
        with col_i:
            st.markdown(f"**{item['başlık']}**")
            st.caption(f"🗞️ {item['kaynak']}  •  🕐 {item['tarih']}")
            if item.get("özet"):
                st.markdown(f"<span style='color:#8b949e;font-size:13px'>{item['özet'][:220]}...</span>",
                            unsafe_allow_html=True)
        with col_l:
            if item.get("link"): st.markdown(f"[🔗 Oku]({item['link']})")
        st.markdown("---")


def render_ai_ranking(results: list):
    """AI MASTER_SCORE sıralaması — en güçlü fırsatlar üstte."""
    st.markdown("<div class='sec-title'>🤖 AI Master Score Sıralaması</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B8FAE;font-size:13px'>Ensemble AI + Teknik + Temel + Akıllı Para bileşenlerinin ağırlıklı ortalaması. En yüksek skorlu hisseler öne çıkar.</p>",
                unsafe_allow_html=True)
    sorted_r = sorted(results, key=lambda x: x["score"]["master"], reverse=True)
    for r in sorted_r[:15]:
        sc   = r["score"]
        css  = score_css(sc["master"])
        sym  = r["sym"].replace(".IS","")
        pct  = sc["master"]
        bar_color = ("#10B981" if pct >= 72 else "#1A56DB" if pct >= 58 else
                     "#6B8FAE" if pct >= 46 else "#EF4444")
        smart_txt = ("🟢 Birikim" if r["smart_money"] == 1 else
                     "🔴 Dağıtım" if r["smart_money"] == -1 else "⚪ Nötr")
        squeeze_txt = "🟡 Sıkışma" if r["squeeze"] else ""
        st.markdown(f"""
<div class='ai-card'>
  <div class='ai-card-header'>
    <span class='ai-sym'>{sym}</span>
    <span class='mscore-badge {css}'>{sc['signal']}</span>
  </div>
  <div style='color:#6B8FAE;font-size:12px;margin-bottom:6px'>
    {r['sektör']} &nbsp;|&nbsp; Fiyat: <b style='color:#C9D1D9'>{r['price']:.2f} TL</b>
    &nbsp;|&nbsp; {smart_txt} {squeeze_txt}
  </div>
  <div style='display:flex;gap:18px;font-size:12px;color:#8AABCC;margin-bottom:8px'>
    <span>🤖 AI: <b style='color:#60A5FA'>{sc['ai']}</b></span>
    <span>📊 Teknik: <b style='color:#60A5FA'>{sc['tech']}</b></span>
    <span>📋 Temel: <b style='color:#60A5FA'>{sc['fund_s']}</b></span>
    <span>💰 Para: <b style='color:#60A5FA'>{sc['smart']}</b></span>
    <span>⚡ Kelly: <b style='color:#FBBF24'>%{r['kelly_frac']}</b></span>
  </div>
  <div class='ai-score-bar'>
    <div class='ai-score-fill' style='width:{pct}%;background:{bar_color};height:6px;border-radius:3px'></div>
  </div>
  <div style='text-align:right;font-family:"IBM Plex Mono",monospace;font-size:12px;color:{bar_color};margin-top:4px'>{pct} / 100</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# KATMAN 12: ANA DÖNGÜ & SIDEBAR
# ─────────────────────────────────────────────────────────────────────

# ── HEADER ──
st.markdown("""
<div class='uq-header'>
  <h1>⚡ BİST ULTIMATE QUANT TERMINAL v1.0 — KURUMSAL EDİSYON</h1>
  <div class='sub'>bistv23pro + rbta10 Tam Birleşimi &nbsp;|&nbsp;
  Ensemble AI &nbsp;|&nbsp; Kelly Pozisyon &nbsp;|&nbsp; Akıllı Para Analizi &nbsp;|&nbsp; Multi-Timeframe</div>
  <div class='badges'>
    <span class='badge g'>✅ Gerçek Zamanlı</span>
    <span class='badge'>⚡ curl_cffi Yahoo API</span>
    <span class='badge p'>🤖 Ensemble AI</span>
    <span class='badge y'>🛡️ Kelly Pozisyon</span>
    <span class='badge g'>📡 Ban-Bypass Aktif</span>
    <span class='badge'>💰 Akıllı Para Takibi</span>
    <span class='badge p'>🔬 Bollinger Squeeze</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
st.sidebar.markdown("""
<div style='text-align:center;padding:8px 0 14px;border-bottom:1px solid #161B22;margin-bottom:10px'>
  <div style='font-size:24px'>⚡</div>
  <div style='color:#C5D8EE;font-weight:700;font-size:15px;margin-top:4px'>BİST Ultimate</div>
  <div style='color:#4B7EB8;font-size:11px'>v1.0 Kurumsal Sürüm</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.success("✅ AI + Teknik Hibrit Motor Aktif")

mkt_status_txt, mkt_desc, mkt_time = market_status()
st.sidebar.markdown("---")
st.sidebar.markdown(f"### {mkt_status_txt} Piyasa")
st.sidebar.markdown(f"**{mkt_desc}**  •  {mkt_time} TR")
st.sidebar.markdown("---")

index_trend   = st.sidebar.selectbox("XU100 Endeks Yönü", ["POZİTİF","NEGATİF"], index=0)
use_ai        = st.sidebar.checkbox("🤖 Ensemble AI Motor (sklearn gerekli)", value=False)
auto_refresh  = st.sidebar.checkbox("⏱️ 5 Dakikada Bir Yenile", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size:11.5px;color:#4B7EB8;line-height:1.85'>
<b style='color:#6B8FAE'>⚡ MASTER SCORE Eşikleri</b><br>
🟢 ≥72 → Güçlü Al<br>
🔵 58-71 → Al<br>
⚪ 46-57 → Tut<br>
🔴 32-45 → Sat<br>
💀 &lt;32 → Güçlü Sat<br><br>
<b style='color:#6B8FAE'>🤖 AI Bileşenler</b><br>
XGBoost + LightGBM<br>
CatBoost + RandomForest<br>
Kelly Pozisyon Boyutu<br><br>
<span style='color:#374151;font-size:10px'>
Sadece bilgilendirme amaçlıdır.<br>
Yatırım tavsiyesi değildir.
</span>
</div>
""", unsafe_allow_html=True)

# ── TARAMA ──


# ─────────────────────────────────────────────────────────────────────
# KATMAN 12: CACHE'Lİ ANA ANALİZ FONKSİYONU
# ─────────────────────────────────────────────────────────────────────
# Tüm ağır iş burada toplanıyor.
# ttl=3600 → 1 saat boyunca sonuç önbellekte kalır.
# Bu süre içinde her tıklama, her sekme değişimi ANİNDA açılır.
# 1 saat dolunca (veya "Yenile" butonuna basılınca) yeniden çalışır.

@st.cache_data(ttl=3600, show_spinner=False)
def run_full_analysis(index_trend: str, use_ai: bool):
    """
    Tüm BİST hisselerini analiz et, sonuçları döndür.
    Streamlit bu fonksiyonu 1 saat boyunca önbellekte tutar.
    Aynı parametrelerle tekrar çağrılırsa anında döner.
    """
    hisseler = list(SECTOR_MAP.keys())
    results  = []

    prog_placeholder = st.empty()
    stat_placeholder = st.empty()

    xu100_df = fetch_market_data("XU100.IS", "1y", "1d")
    usd_df   = fetch_market_data("TRY=X",    "1y", "1d")

    global_models = None
    raw_cache: dict = {}

    stat_placeholder.info("📥 Veriler çekiliyor, lütfen bekleyin...")

    # Geçiş 1: veri çek
    for idx, sym in enumerate(hisseler):
        prog_placeholder.progress(
            (idx + 1) / len(hisseler) * 0.5,
            text=f"📥 Veri çekiliyor: {sym}  ({idx+1}/{len(hisseler)})"
        )
        raw_df = fetch_market_data(sym, "1y", "1d")
        if not raw_df.empty and len(raw_df) >= 50:
            raw_cache[sym] = raw_df

    # AI eğitimi
    if use_ai and SKLEARN_AVAILABLE and raw_cache:
        stat_placeholder.info("🤖 Ensemble AI eğitiliyor...")
        frames = []
        for sym, raw_df in raw_cache.items():
            try:
                df_tmp = raw_df.copy()
                df_tmp.columns = [str(c).strip().title() for c in df_tmp.columns]
                df_tmp = calculate_indicators(df_tmp)
                df_tmp = build_target(df_tmp)
                df_tmp.dropna(subset=FEATURE_COLS + ["TARGET"], inplace=True)
                if len(df_tmp) >= 80:
                    frames.append(df_tmp)
            except Exception:
                pass
        if frames:
            combined = pd.concat(frames).sort_index() if len(frames) >= 3 else frames[0]
            if len(combined) >= 120:
                try:
                    global_models = train_ensemble(combined)
                except Exception:
                    global_models = None

    # Geçiş 2: analiz
    for idx, sym in enumerate(hisseler):
        prog_placeholder.progress(
            0.5 + (idx + 1) / len(hisseler) * 0.5,
            text=f"⚡ Analiz ediliyor: {sym}  ({idx+1}/{len(hisseler)})"
        )
        raw_df = raw_cache.get(sym)
        if raw_df is not None:
            res = analyze(sym, raw_df, global_models, xu100_df, usd_df, index_trend)
            if res:
                results.append(res)

    prog_placeholder.empty()
    stat_placeholder.empty()
    return results


# ─────────────────────────────────────────────────────────────────────
# KATMAN 13: ANA SAYFA & SIDEBAR
# ─────────────────────────────────────────────────────────────────────

# ── HEADER ──
st.markdown("""
<div class='uq-header'>
  <h1>⚡ BİST ULTIMATE QUANT TERMINAL v1.0 — KURUMSAL EDİSYON</h1>
  <div class='sub'>bistv23pro + rbta10 Tam Birleşimi &nbsp;|&nbsp;
  Ensemble AI &nbsp;|&nbsp; Kelly Pozisyon &nbsp;|&nbsp; Akıllı Para Analizi &nbsp;|&nbsp; Multi-Timeframe</div>
  <div class='badges'>
    <span class='badge g'>✅ Gerçek Zamanlı</span>
    <span class='badge'>⚡ curl_cffi Yahoo API</span>
    <span class='badge p'>🤖 Ensemble AI</span>
    <span class='badge y'>🛡️ Kelly Pozisyon</span>
    <span class='badge g'>📡 Ban-Bypass Aktif</span>
    <span class='badge'>💰 Akıllı Para Takibi</span>
    <span class='badge p'>🔬 Bollinger Squeeze</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
st.sidebar.markdown("""
<div style='text-align:center;padding:8px 0 14px;border-bottom:1px solid #161B22;margin-bottom:10px'>
  <div style='font-size:24px'>⚡</div>
  <div style='color:#C5D8EE;font-weight:700;font-size:15px;margin-top:4px'>BİST Ultimate</div>
  <div style='color:#4B7EB8;font-size:11px'>v1.0 Kurumsal Sürüm</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.success("✅ AI + Teknik Hibrit Motor Aktif")

mkt_status_txt, mkt_desc, mkt_time = market_status()
st.sidebar.markdown("---")
st.sidebar.markdown(f"### {mkt_status_txt} Piyasa")
st.sidebar.markdown(f"**{mkt_desc}**  •  {mkt_time} TR")
st.sidebar.markdown("---")

index_trend  = st.sidebar.selectbox("XU100 Endeks Yönü", ["POZİTİF","NEGATİF"], index=0)
use_ai       = st.sidebar.checkbox("🤖 Ensemble AI Motor (sklearn gerekli)", value=False)
auto_refresh = st.sidebar.checkbox("⏱️ 5 Dakikada Bir Yenile", value=False)

# ── VERİLERİ YENİLE BUTONU ──
if st.sidebar.button("🔄 Verileri Şimdi Yenile"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("""
<div style='font-size:11px;color:#4B7EB8;margin-top:8px;padding:8px;background:rgba(26,86,219,0.08);border-radius:8px;border:1px solid rgba(26,86,219,0.2)'>
⏱️ Veriler <b style='color:#60A5FA'>1 saatte bir</b> otomatik güncellenir.<br>
Manuel güncelleme için yukarıdaki butonu kullanın.
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size:11.5px;color:#4B7EB8;line-height:1.85'>
<b style='color:#6B8FAE'>⚡ MASTER SCORE Eşikleri</b><br>
🟢 ≥72 → Güçlü Al<br>
🔵 58-71 → Al<br>
⚪ 46-57 → Tut<br>
🔴 32-45 → Sat<br>
💀 &lt;32 → Güçlü Sat<br><br>
<b style='color:#6B8FAE'>🤖 AI Bileşenler</b><br>
XGBoost + LightGBM<br>
CatBoost + RandomForest<br>
Kelly Pozisyon Boyutu<br><br>
<span style='color:#374151;font-size:10px'>
Sadece bilgilendirme amaçlıdır.<br>
Yatırım tavsiyesi değildir.
</span>
</div>
""", unsafe_allow_html=True)

# ── ANALİZİ ÇALIŞTIR (önbellekten veya hesaplayarak) ──
with st.spinner("⚡ Analiz yükleniyor... (İlk açılışta ~3-5 dk, sonraki açılışlar anlık)"):
    results = run_full_analysis(index_trend, use_ai)

if not results:
    st.error("❌ Hiçbir hisse verisi çekilemedi. Bağlantınızı kontrol edin.")
    st.stop()

# ── TABLAR ──
tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Platform",
    "🤖 AI Sıralaması",
    "🔄 Sektörel Rotasyon",
    "🎯 Hisse Analiz Kartı",
    "🕯️ Grafik Stüdyosu",
    "💼 Portföy Takip",
    "📰 Haberler",
])

with tab0:
    st.markdown("""
<div style='max-width:920px;margin:0 auto'>
<div class='sec-title'>BİST Ultimate Quant Terminal Nedir?</div>
<p style='color:#8AABCC;font-size:14px;line-height:1.85'>
Bu platform, iki profesyonel analiz motorunun (<b style='color:#C5D8EE'>bistv23pro</b> ve
<b style='color:#C5D8EE'>rbta10</b>) birleşiminden doğan kurumsal düzeyde bir BİST analiz terminalidir.
Gerçek zamanlı Yahoo Finance verileri <b>curl_cffi</b> ile ban-proof olarak çekilir,
<b>Ensemble AI</b> modeli (XGBoost + LightGBM + CatBoost + RandomForest) sinyal üretir,
<b>Kelly Kriteri</b> ile optimal pozisyon boyutu hesaplanır.
</p>
</div>
""", unsafe_allow_html=True)
    st.markdown("""
<div class='stat-row'>
  <div class='stat-box'><div class='stat-num'>50+</div><div class='stat-lbl'>BIST Hissesi</div></div>
  <div class='stat-box'><div class='stat-num'>4</div><div class='stat-lbl'>Ensemble AI Modeli</div></div>
  <div class='stat-box'><div class='stat-num'>15+</div><div class='stat-lbl'>Teknik Gösterge</div></div>
  <div class='stat-box'><div class='stat-num'>3</div><div class='stat-lbl'>Zaman Dilimi (MTF)</div></div>
  <div class='stat-box'><div class='stat-num'>%100</div><div class='stat-lbl'>Türkçe Arayüz</div></div>
</div>

<div class='sec-title'>MASTER_SCORE Bileşenleri</div>
<table style='width:100%;border-collapse:collapse;color:#8AABCC;font-size:13px'>
  <thead><tr style='background:#0C1725;color:#60A5FA'>
    <th style='padding:9px;border:1px solid #161B22;text-align:left'>Bileşen</th>
    <th style='padding:9px;border:1px solid #161B22'>Ağırlık</th>
    <th style='padding:9px;border:1px solid #161B22;text-align:left'>İçerik</th>
  </tr></thead>
  <tbody>
    <tr><td style='padding:8px;border:1px solid #161B22'><b style='color:#C5D8EE'>🤖 AI Skoru</b></td>
        <td style='text-align:center;border:1px solid #161B22;color:#34D399'>%30</td>
        <td style='padding:8px;border:1px solid #161B22'>XGB+LGBM+CatBoost+RF ensemble olasılığı</td></tr>
    <tr><td style='padding:8px;border:1px solid #161B22'><b style='color:#C5D8EE'>📊 Teknik Skor</b></td>
        <td style='text-align center;border:1px solid #161B22;color:#60A5FA'>%35</td>
        <td style='padding:8px;border:1px solid #161B22'>EMA, MACD, RSI, Bollinger — rejim-ağırlıklı</td></tr>
    <tr><td style='padding:8px;border:1px solid #161B22'><b style='color:#C5D8EE'>📋 Temel Skor</b></td>
        <td style='text-align:center;border:1px solid #161B22;color:#FBBF24'>%15</td>
        <td style='padding:8px;border:1px solid #161B22'>F/K, PD/DD, ROE canlı verisi</td></tr>
    <tr><td style='padding:8px;border:1px solid #161B22'><b style='color:#C5D8EE'>💰 Akıllı Para</b></td>
        <td style='text-align:center;border:1px solid #161B22;color:#C084FC'>%20</td>
        <td style='padding:8px;border:1px solid #161B22'>OBV kırılım, MFI, Smart Money Flow, Squeeze</td></tr>
  </tbody>
</table>

<div class='warn-box' style='margin-top:20px'>
  ⚠️ <b>Yasal Uyarı:</b> Bu platform yalnızca bilgilendirme ve araştırma amaçlıdır.
  Üretilen sinyaller yatırım tavsiyesi niteliği taşımaz. Tüm yatırım kararları
  yatırımcının kendi sorumluluğundadır. Geçmiş performans gelecekteki sonuçların
  garantisi değildir.
</div>
</div>
""", unsafe_allow_html=True)

with tab1:
    render_ai_ranking(results)

with tab2:
    s_data = {}
    for r in results:
        sec = r["sektör"]
        if sec not in s_data:
            s_data[sec] = {"sc": [], "chg": [], "h": []}
        s_data[sec]["sc"].append(r["score"]["master"])
        s_data[sec]["chg"].append(r["chg"])
        s_data[sec]["h"].append(r["sym"].replace(".IS",""))
    sec_rows = []
    for k, v in s_data.items():
        asc   = sum(v["sc"]) / len(v["sc"])
        achg  = sum(v["chg"]) / len(v["chg"])
        sec_rows.append({
            "Sektör":              k,
            "Ort. Master Skor":    int(asc),
            "Sektör Momentumu (%)": round(achg, 2),
            "Göreceli Güç (RS)":   round(asc * 0.6 + achg * 0.4, 2),
            "Hisseler":            ", ".join(v["h"]),
        })
    df_sec = (pd.DataFrame(sec_rows)
              .sort_values("Göreceli Güç (RS)", ascending=False)
              .reset_index(drop=True))
    st.markdown("<div class='sec-title'>🔄 BİST Sektörel Rotasyon Liderlik Paneli</div>",
                unsafe_allow_html=True)
    if not df_sec.empty:
        st.success(f"👑 **Lider Sektör:** {df_sec.iloc[0]['Sektör']}")
        show_table(df_sec, score_col="Ort. Master Skor")
    st.divider()
    render_screener(results)

with tab3:
    st.markdown("<div class='sec-title'>🎯 Hisse Analiz Kartı</div>", unsafe_allow_html=True)
    sel_sym = st.selectbox("Hisse Seçin:", [r["sym"] for r in results],
                           format_func=lambda x: x.replace(".IS",""))
    r_sel = next((r for r in results if r["sym"] == sel_sym), None)
    if r_sel:
        render_hisse_kart(r_sel)

with tab4:
    render_advanced_chart_tab(results)

with tab5:
    render_portfolio_tab(results)

with tab6:
    render_news_tab(results)

if auto_refresh:
    time.sleep(300)
    st.cache_data.clear()
    st.rerun()
