# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════════════════╗
# ║   BİST ULTIMATE QUANT TERMINAL v1.0 — STREAMLIT ARAYÜZÜ            ║
# ║   Çalıştır: streamlit run app.py                                    ║
# ║                                                                     ║
# ║   Bu dosya SADECE motor.py'nin ürettiği JSON'u okur.                ║
# ║   Hiç internet isteği göndermez → saniyeler içinde açılır.          ║
# ╚══════════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import json
import time
from datetime import datetime, timedelta

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
# CSS
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
[data-testid="stTabs"] button {
    font-family: 'IBM Plex Sans', sans-serif !important; font-size: 13px !important;
    font-weight: 500 !important; color: #6B8FAE !important; padding: 10px 18px !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #60A5FA !important; border-bottom: 2px solid #1A56DB !important;
}
[data-testid="stMetric"] {
    background: #0C1725 !important; border: 1px solid #161B22 !important;
    border-radius: 10px !important; padding: 12px 16px !important;
}
[data-testid="stMetricLabel"] { color: #6B8FAE !important; font-size: 12px !important; }
[data-testid="stMetricValue"] {
    color: #E2EBF6 !important; font-size: 19px !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.mscore-badge {
    display: inline-block; padding: 4px 14px; border-radius: 20px;
    font-family: 'IBM Plex Mono', monospace; font-size: 13px; font-weight: 700;
}
.mscore-bull   { background: rgba(16,185,129,0.18); border: 1px solid #10B981; color: #34D399; }
.mscore-buy    { background: rgba(26,86,219,0.18);  border: 1px solid #1A56DB; color: #60A5FA; }
.mscore-hold   { background: rgba(107,143,174,0.18);border: 1px solid #6B8FAE; color: #94A3B8; }
.mscore-sell   { background: rgba(239,68,68,0.14);  border: 1px solid #EF4444; color: #FCA5A5; }
.mscore-danger { background: rgba(239,68,68,0.22);  border: 1px solid #DC2626; color: #F87171; }
.sec-title {
    font-size: 17px; font-weight: 600; color: #C5D8EE;
    border-left: 3px solid #1A56DB; padding-left: 12px; margin: 22px 0 12px 0;
}
[data-testid="stExpander"] {
    background: #0A1525 !important; border: 1px solid #161B22 !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] * { color: #8AABCC !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #C5D8EE !important; }
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
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #060A10; }
::-webkit-scrollbar-thumb { background: #161B22; border-radius: 3px; }
.warn-box {
    background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.22);
    border-radius: 10px; padding: 12px 16px; color: #D4A017; font-size: 13px; margin-top: 16px;
}
.stat-row { display: flex; gap: 14px; margin: 18px 0; flex-wrap: wrap; }
.stat-box {
    flex: 1 1 150px; text-align: center; background: #0C1725;
    border: 1px solid #161B22; border-radius: 10px; padding: 16px;
}
.stat-num { font-family: 'IBM Plex Mono', monospace; font-size: 26px; font-weight: 700; color: #60A5FA; }
.stat-lbl { color: #6B8FAE; font-size: 12px; margin-top: 4px; }
.stale-banner {
    background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.4);
    border-radius: 8px; padding: 10px 16px; color: #FBBF24; font-size: 13px; margin-bottom: 16px;
}
.fresh-banner {
    background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.3);
    border-radius: 8px; padding: 10px 16px; color: #34D399; font-size: 13px; margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────────
CACHE_DIR      = os.path.join(os.environ.get("HOME", "/tmp"), "bist_cache")
RESULTS_FILE   = os.path.join(CACHE_DIR, "results.json")
PORTFOLIO_FILE = os.path.join(CACHE_DIR, "portfolio.json")
os.makedirs(CACHE_DIR, exist_ok=True)

SECTOR_MAP = {
    "THYAO.IS": "HAVACILIK",    "PGSUS.IS": "HAVACILIK",
    "AKBNK.IS": "BANKACILIK",   "GARAN.IS": "BANKACILIK",
    "ISCTR.IS": "BANKACILIK",   "YKBNK.IS": "BANKACILIK",
    "HALKB.IS": "BANKACILIK",   "VAKBN.IS": "BANKACILIK",
    "TSKB.IS":  "BANKACILIK",   "QNBFB.IS": "BANKACILIK",
    "EREGL.IS": "DEMİR-ÇELİK", "KRDMD.IS": "DEMİR-ÇELİK",
    "ISDMR.IS": "DEMİR-ÇELİK",
    "TUPRS.IS": "ENERJİ",       "AKSEN.IS": "ENERJİ",
    "ZOREN.IS": "ENERJİ",       "ODAS.IS":  "ENERJİ",
    "ASTOR.IS": "ENERJİ",
    "PETKM.IS": "KİMYA",        "GUBRF.IS": "KİMYA",
    "SODA.IS":  "KİMYA",        "ALKIM.IS": "KİMYA",
    "KCHOL.IS": "HOLDİNG",      "SAHOL.IS": "HOLDİNG",
    "DOHOL.IS": "HOLDİNG",      "SISE.IS":  "HOLDİNG",
    "AGHOL.IS": "HOLDİNG",
    "BIMAS.IS": "PERAKENDE",    "MGROS.IS": "PERAKENDE",
    "SOKM.IS":  "PERAKENDE",
    "ASELS.IS": "SAVUNMA",      "HATEK.IS": "SAVUNMA",
    "TCELL.IS": "TELEKOM",      "TTKOM.IS": "TELEKOM",
    "FROTO.IS": "OTOMOTİV",     "TOASO.IS": "OTOMOTİV",
    "TTRAK.IS": "OTOMOTİV",     "OTKAR.IS": "OTOMOTİV",
    "BRISA.IS": "OTOMOTİV",
    "EMLAK.IS": "GAYRİMENKUL",  "ISGYO.IS": "GAYRİMENKUL",
    "EKGYO.IS": "GAYRİMENKUL",
    "ANHYT.IS": "SİGORTA",      "ANSGR.IS": "SİGORTA",
    "AGESA.IS": "SİGORTA",
    "LOGO.IS":  "TEKNOLOJİ",    "NETAS.IS": "TEKNOLOJİ",
    "ULKER.IS": "GIDA",         "TATGD.IS": "GIDA",
    "CCOLA.IS": "GIDA",         "AEFES.IS": "GIDA",
    "KOZAL.IS": "MADENCİLİK",   "KOZAA.IS": "MADENCİLİK",
    "ARCLK.IS": "EV ALETLERİ",  "VESTL.IS": "EV ALETLERİ",
    "VESBE.IS": "EV ALETLERİ",
    "AKCNS.IS": "ÇİMENTO",      "CIMSA.IS": "ÇİMENTO",
    "BOLUC.IS": "ÇİMENTO",
    "ENKAI.IS": "İNŞAAT",
    "MAVI.IS":  "TEKSTİL",
}


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


def score_css(master: int) -> str:
    if master >= 72: return "mscore-bull"
    if master >= 58: return "mscore-buy"
    if master >= 46: return "mscore-hold"
    if master >= 32: return "mscore-sell"
    return "mscore-danger"


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


def df_from_json(df_json: dict) -> pd.DataFrame:
    """JSON'dan DataFrame geri yükle."""
    df = pd.DataFrame(df_json["data"], columns=df_json["columns"])
    df.index = pd.to_datetime(df_json["index"])
    df.index.name = "Date"
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ─────────────────────────────────────────────────────────────────────
# SONUÇLARI YÜKLE
# ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)   # 5 dakika önbellek — motor yeniden çalışırsa güncellenir
def load_results():
    if not os.path.exists(RESULTS_FILE):
        return None
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────
# BACKTEST (yerel — internet gerektirmez)
# ─────────────────────────────────────────────────────────────────────
def run_backtest(sym: str, df: pd.DataFrame,
                 capital: float = 100_000.0,
                 comm: float = 0.0005,
                 slip: float = 0.0005):
    if df is None or len(df) < 40:
        return None
    bt     = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    cap    = capital
    pos    = 0
    ep     = sl = hp = ps = 0.0
    ed     = None
    trades = []
    eq     = [capital]
    for i in range(20, len(bt) - 1):
        window = bt.iloc[:i + 1].copy()
        cl     = window["Close"]
        ema9   = cl.ewm(span=9,  adjust=False).mean().iloc[-1]
        ema21  = cl.ewm(span=21, adjust=False).mean().iloc[-1]
        delta  = cl.diff()
        gain   = delta.where(delta > 0, 0).rolling(14).mean()
        loss   = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi    = (100 - (100 / (1 + gain / (loss + 1e-9)))).iloc[-1]
        e12    = cl.ewm(span=12, adjust=False).mean()
        e26    = cl.ewm(span=26, adjust=False).mean()
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
        ts  = 50 + (25 if ema9 > ema21 else -25) + (25 if macd_hist > 0 else -25)
        os_ = 50 + (25 if rsi < 30 else (-25 if rsi > 70 else 0))
        sc  = int(ts * 0.6 + os_ * 0.4)
        sig = "AL" if sc >= 60 else ("SAT" if sc <= 40 else "TUT")
        next_row  = bt.iloc[i + 1]
        cd        = bt.index[i + 1]
        exec_open = float(next_row["Open"])
        if pos == 1:
            if cur_close > hp:
                hp  = cur_close
                nsl = hp - 2.0 * atr
                if nsl > sl:
                    sl = nsl
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
# GRAFİKLER
# ─────────────────────────────────────────────────────────────────────
def make_candle_chart(r: dict):
    df  = df_from_json(r["df_json"]).tail(60)
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
# RENDER FONKSİYONLARI
# ─────────────────────────────────────────────────────────────────────
def render_hisse_kart(r: dict):
    sc   = r["score"]
    sym  = r["sym"].replace(".IS", "")
    css  = score_css(sc["master"])
    st.markdown(f"<div class='sec-title'>🎯 {sym} — Master Analiz Kartı</div>",
                unsafe_allow_html=True)
    col_s, col_ai, col_t, col_f, col_sm = st.columns(5)
    col_s.metric("⚡ MASTER SCORE", f"{sc['master']} / 100")
    col_ai.metric("🤖 AI Olasılık", f"%{r['ai_prob']}")
    col_t.metric("📊 Teknik Skor",  f"{sc['tech']} / 100")
    col_f.metric("📋 Temel Skor",   f"{sc['fund_s']} / 100")
    col_sm.metric("💰 Akıllı Para", f"{sc['smart']} / 100")
    st.markdown(f"""
<div style='text-align:center;margin:10px 0'>
  <span class='mscore-badge {css}' style='font-size:16px;padding:8px 28px'>{sc['signal']}</span>
</div>
""", unsafe_allow_html=True)
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
    squeeze_ic  = "🟡 AKTİF" if r["squeeze"]     else "⚪ YOK"
    smart_ic    = ("🟢 BİRİKİM" if r["smart_money"] == 1
                   else "🔴 DAĞITIM" if r["smart_money"] == -1 else "⚪ NÖTR")
    obv_ic      = "🟢 YUKARI" if r["obv_break"] else "⚪ ALTTA"
    s1, s2, s3 = st.columns(3)
    s1.metric("Bollinger Sıkışma", squeeze_ic)
    s2.metric("Akıllı Para Akışı", smart_ic)
    s3.metric("OBV Kırılım",       obv_ic)
    st.plotly_chart(make_candle_chart(r), use_container_width=True)
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
    with st.expander("🛡️ Risk Yönetimi & Pozisyon Boyutlandırması", expanded=False):
        st.markdown(tip("**Risk Parametreleri**", "ATR Stop & Kelly",
            "ATR Stop: Kapanışın 2×ATR altı. Kelly: Optimal sermaye yüzdesi. "
            "ATR Lot: 100k TL sermayede %1 risk ile alınabilecek tahmini lot."),
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
    with st.expander("📈 Backtest Raporu (1Y, 100.000 TL başlangıç)", expanded=False):
        df_bt = df_from_json(r["df_json"])
        bt = run_backtest(r["sym"], df_bt)
        if bt:
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Net Getiri",   f"%{bt['total_return']:.2f}")
            b2.metric("Max Drawdown", f"%{bt['max_drawdown']:.2f}")
            b3.metric("Win Rate",     f"%{bt['win_rate']:.1f}")
            b4.metric("Nihai Değer",  f"{bt['final_value']:,.0f} TL")
            st.plotly_chart(make_equity_chart(bt["equity_curve"], r["sym"]),
                            use_container_width=True)
            if not bt["trades"].empty:
                show_table(bt["trades"].tail(5).reset_index(drop=True))


def render_screener(results: list):
    st.markdown("<div class='sec-title'>🔍 MASTER SCORE Akıllı Tarayıcı</div>",
                unsafe_allow_html=True)
    cf1, cf2, cf3, cf4 = st.columns(4)
    with cf1:
        f_sig = st.multiselect("Sinyal",
            ["⚡ GÜÇLÜ AL","🟢 AL","🟡 TUT","🔴 SAT","💀 GÜÇLÜ SAT"],
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
        sc = r["score"]
        df_bt = df_from_json(r["df_json"])
        bt = run_backtest(r["sym"], df_bt)
        rows.append({
            "Hisse":         r["sym"].replace(".IS",""),
            "Sektör":        r["sektör"],
            "Master Skor":   sc["master"],
            "AI Sinyali":    sc["signal"],
            "AI (%)":        r["ai_prob"],
            "Teknik":        sc["tech"],
            "Akıllı Para":   sc["smart"],
            "Rejim":         r["regime"],
            "Trend Uyumu":   r["mtf"]["alignment_score"],
            "BT Return (%)": round(bt["total_return"], 2) if bt else 0.0,
            "MaxDD (%)":     round(bt["max_drawdown"],  2) if bt else 0.0,
        })
    df_s = pd.DataFrame(rows)
    if not df_s.empty:
        if f_sig:  df_s = df_s[df_s["AI Sinyali"].isin(f_sig)]
        if f_reg:  df_s = df_s[df_s["Rejim"].isin(f_reg)]
        df_s = df_s[df_s["Trend Uyumu"] >= m_align]
        df_s = df_s[df_s["AI (%)"]      >= min_ai]
        show_table(df_s.sort_values("Master Skor", ascending=False).reset_index(drop=True),
                   score_col="Master Skor")


def render_ai_ranking(results: list):
    st.markdown("<div class='sec-title'>🤖 AI Master Score Sıralaması</div>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#6B8FAE;font-size:13px'>Ensemble AI + Teknik + Temel + Akıllı Para. "
                "En yüksek skorlu hisseler öne çıkar.</p>", unsafe_allow_html=True)
    sorted_r = sorted(results, key=lambda x: x["score"]["master"], reverse=True)
    for r in sorted_r[:15]:
        sc  = r["score"]
        css = score_css(sc["master"])
        sym = r["sym"].replace(".IS","")
        pct = sc["master"]
        bar_color = ("#10B981" if pct >= 72 else "#1A56DB" if pct >= 58 else
                     "#6B8FAE" if pct >= 46 else "#EF4444")
        smart_txt   = ("🟢 Birikim" if r["smart_money"] == 1 else
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


def render_advanced_chart_tab(results: list):
    st.markdown("<div class='sec-title'>🕯️ Gelişmiş Grafik & Teknik Analiz Stüdyosu</div>",
                unsafe_allow_html=True)
    col_sym, col_bars = st.columns(2)
    with col_sym:
        sel = st.selectbox("Hisse", [r["sym"] for r in results],
                           format_func=lambda x: x.replace(".IS",""), key="adv_sym")
    with col_bars:
        bars = st.slider("Bar Sayısı", 30, 365, 120, key="adv_bars")
    inds = st.multiselect("Göstergeler",
        ["EMA9","EMA21","EMA50","Bollinger","RSI","MACD","Stochastic","OBV","MFI"],
        default=["EMA21","EMA50","Bollinger","RSI","MACD","MFI"], key="adv_inds")
    r = next((x for x in results if x["sym"] == sel), None)
    if not r:
        st.warning("Hisse verisi bulunamadı.")
        return
    df_adv = df_from_json(r["df_json"])
    st.plotly_chart(make_advanced_chart(df_adv, sel, inds, bars), use_container_width=True)
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
        with pc1: p_sym  = st.selectbox("Hisse", sorted(set(all_syms)),
                                         format_func=lambda x: x.replace(".IS",""), key="p_sym")
        with pc2: p_lot  = st.number_input("Adet", min_value=1, value=100, key="p_lot")
        with pc3: p_cost = st.number_input("Alış Fiyatı", min_value=0.01, value=10.0,
                                            format="%.2f", key="p_cost")
        with pc4: p_date = st.date_input("Alış Tarihi", key="p_date")
        if st.button("✅ Portföye Ekle"):
            portfolio.append({"hisse": p_sym, "lot": int(p_lot),
                              "maliyet": round(float(p_cost), 2), "tarih": str(p_date)})
            st.session_state.portfolio = portfolio
            try:
                with open(PORTFOLIO_FILE, "w") as f:
                    json.dump(portfolio, f, ensure_ascii=False)
            except Exception:
                pass
            st.success(f"{p_sym.replace('.IS','')} eklendi!")
            st.rerun()
    if not portfolio:
        st.info("Henüz pozisyon yok. Yukarıdan ekleyin.")
        return
    # Anlık fiyatı results'tan al (internet gerekmez)
    price_map = {r["sym"]: r["price"] for r in results}
    rows = []
    tot_cost = tot_cur = 0.0
    for pos in portfolio:
        sym  = pos["hisse"]
        lot  = pos["lot"]
        cost = pos["maliyet"]
        cur  = price_map.get(sym, cost)
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
    m3.metric("Toplam K/Z", f"{pnl:,.0f} TL", delta=f"%{pnl/tot_cost*100:.2f}")
    m4.metric("Pozisyon", str(len(portfolio)))
    if len(rows) > 1:
        st.plotly_chart(make_portfolio_pie([{"hisse": r["Hisse"],
                                             "maliyet": r["Maliyet (TL)"]} for r in rows]),
                        use_container_width=True)
    with st.expander("🗑️ Pozisyon Sil"):
        opts = [f"{p['hisse'].replace('.IS','')} — {p['lot']} lot @ {p['maliyet']}"
                for p in portfolio]
        sel_d = st.selectbox("Sil:", opts, key="del_sel")
        if st.button("❌ Sil"):
            portfolio.pop(opts.index(sel_d))
            st.session_state.portfolio = portfolio
            try:
                with open(PORTFOLIO_FILE, "w") as f:
                    json.dump(portfolio, f, ensure_ascii=False)
            except Exception:
                pass
            st.success("Silindi.")
            st.rerun()


def render_news_tab():
    """Haberler — motor.py çalıştığında news_cache.json'dan okur."""
    st.markdown("<div class='sec-title'>📰 Piyasa Haberleri & Gündem</div>",
                unsafe_allow_html=True)
    news_cache = os.path.join(CACHE_DIR, "news_cache.json")
    if os.path.exists(news_cache):
        try:
            with open(news_cache, "r", encoding="utf-8") as f:
                news = json.load(f)
            st.info(f"📡 Son güncelleme: {news.get('timestamp', '—')}")
            for item in news.get("items", [])[:15]:
                col_i, col_l = st.columns([5, 1])
                with col_i:
                    st.markdown(f"**{item['başlık']}**")
                    st.caption(f"🗞️ {item['kaynak']}  •  🕐 {item['tarih']}")
                    if item.get("özet"):
                        st.markdown(
                            f"<span style='color:#8b949e;font-size:13px'>{item['özet'][:220]}...</span>",
                            unsafe_allow_html=True)
                with col_l:
                    if item.get("link"):
                        st.markdown(f"[🔗 Oku]({item['link']})")
                st.markdown("---")
            return
        except Exception:
            pass
    st.warning("📡 Haber verisi henüz yok. `motor.py`'yi çalıştırın veya `motor.py`'ye "
               "`fetch_news` çağrısı ekleyin.")


# ─────────────────────────────────────────────────────────────────────
# ANA SAYFA
# ─────────────────────────────────────────────────────────────────────

# ── HEADER ──
st.markdown("""
<div class='uq-header'>
  <h1>⚡ BİST ULTIMATE QUANT TERMINAL v1.0 — KURUMSAL EDİSYON</h1>
  <div class='sub'>bistv23pro + rbta10 Tam Birleşimi &nbsp;|&nbsp;
  Ensemble AI &nbsp;|&nbsp; Kelly Pozisyon &nbsp;|&nbsp; Akıllı Para Analizi &nbsp;|&nbsp; Multi-Timeframe</div>
  <div class='badges'>
    <span class='badge g'>✅ Önbellekten Hızlı Yükleme</span>
    <span class='badge'>⚡ motor.py Mimarisi</span>
    <span class='badge p'>🤖 Ensemble AI</span>
    <span class='badge y'>🛡️ Kelly Pozisyon</span>
    <span class='badge g'>📡 Ban-Bypass Aktif</span>
    <span class='badge'>💰 Akıllı Para Takibi</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
st.sidebar.markdown("""
<div style='text-align:center;padding:8px 0 14px;border-bottom:1px solid #161B22;margin-bottom:10px'>
  <div style='font-size:24px'>⚡</div>
  <div style='color:#C5D8EE;font-weight:700;font-size:15px;margin-top:4px'>BİST Ultimate</div>
  <div style='color:#4B7EB8;font-size:11px'>v1.0 — motor.py Mimarisi</div>
</div>
""", unsafe_allow_html=True)

mkt_status_txt, mkt_desc, mkt_time = market_status()
st.sidebar.markdown("---")
st.sidebar.markdown(f"### {mkt_status_txt} Piyasa")
st.sidebar.markdown(f"**{mkt_desc}**  •  {mkt_time} TR")
st.sidebar.markdown("---")

# Motor güncelleme butonu
if st.sidebar.button("🔄 Motoru Şimdi Çalıştır"):
    st.sidebar.info("Terminal üzerinde `python motor.py --ai` komutunu çalıştırın.")

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
<b style='color:#6B8FAE'>⏱️ Güncelleme Döngüsü</b><br>
motor.py → results.json<br>
Cron veya manual çalıştırın<br><br>
<span style='color:#374151;font-size:10px'>
Sadece bilgilendirme amaçlıdır.<br>
Yatırım tavsiyesi değildir.
</span>
</div>
""", unsafe_allow_html=True)

# ── SONUÇLARI YÜKLE ──
payload = load_results()

if payload is None:
    st.error("❌ Veri dosyası bulunamadı.")
    st.markdown("""
<div class='warn-box'>
  <b>İlk çalıştırma:</b> Terminalde şu komutu çalıştırın:<br><br>
  <code style='background:#0A1628;padding:4px 10px;border-radius:6px;color:#60A5FA'>
  python motor.py
  </code><br><br>
  AI motoru ile (daha uzun sürer ama daha iyi sinyaller):<br>
  <code style='background:#0A1628;padding:4px 10px;border-radius:6px;color:#60A5FA'>
  python motor.py --ai
  </code><br><br>
  motor.py tamamlandığında bu sayfa otomatik olarak yenilenir.
</div>
""", unsafe_allow_html=True)
    st.stop()

results     = payload["results"]
ts_str      = payload.get("timestamp", "")
index_trend = payload.get("index_trend", "POZİTİF")
use_ai      = payload.get("use_ai", False)

# Veri tazeliği göstergesi
try:
    ts_dt   = datetime.fromisoformat(ts_str)
    age_min = int((datetime.now() - ts_dt).total_seconds() / 60)
    if age_min > 120:
        st.markdown(
            f"<div class='stale-banner'>⚠️ Veriler <b>{age_min} dakika</b> önce güncellendi. "
            f"Taze veri için <code>python motor.py</code> çalıştırın.</div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div class='fresh-banner'>✅ Veriler <b>{age_min} dakika</b> önce güncellendi — "
            f"{len(results)} hisse &nbsp;|&nbsp; Endeks: {index_trend} "
            f"&nbsp;|&nbsp; AI: {'Aktif 🤖' if use_ai else 'Kural tabanlı'}</div>",
            unsafe_allow_html=True)
except Exception:
    pass

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
Bu platform, <b style='color:#C5D8EE'>motor.py + app.py</b> iki katmanlı mimarisiyle çalışır.
Ağır hesaplamalar (veri çekme, Ensemble AI, indikatörler) <b>motor.py</b> tarafından arka planda
yapılır ve <code>results.json</code> dosyasına kaydedilir. Streamlit arayüzü bu dosyayı okuyarak
saniyeler içinde açılır — her tıklamada internet isteği gitmez.
</p>
</div>
""", unsafe_allow_html=True)
    st.markdown("""
<div class='stat-row'>
  <div class='stat-box'><div class='stat-num'>2</div><div class='stat-lbl'>Katmanlı Mimari</div></div>
  <div class='stat-box'><div class='stat-num'>4</div><div class='stat-lbl'>Ensemble AI Modeli</div></div>
  <div class='stat-box'><div class='stat-num'>15+</div><div class='stat-lbl'>Teknik Gösterge</div></div>
  <div class='stat-box'><div class='stat-num'>0</div><div class='stat-lbl'>UI'da API İsteği</div></div>
  <div class='stat-box'><div class='stat-num'>%100</div><div class='stat-lbl'>Türkçe Arayüz</div></div>
</div>
<div class='sec-title'>Çalışma Mimarisi</div>
<table style='width:100%;border-collapse:collapse;color:#8AABCC;font-size:13px'>
  <thead><tr style='background:#0C1725;color:#60A5FA'>
    <th style='padding:9px;border:1px solid #161B22;text-align:left'>Dosya</th>
    <th style='padding:9px;border:1px solid #161B22;text-align:left'>Görev</th>
    <th style='padding:9px;border:1px solid #161B22;text-align:left'>Ne Zaman</th>
  </tr></thead>
  <tbody>
    <tr><td style='padding:8px;border:1px solid #161B22'><b style='color:#C5D8EE'>motor.py</b></td>
        <td style='padding:8px;border:1px solid #161B22'>Veri çekme + AI + Analiz → results.json</td>
        <td style='padding:8px;border:1px solid #161B22'>Cron ile saatlik veya manual</td></tr>
    <tr><td style='padding:8px;border:1px solid #161B22'><b style='color:#C5D8EE'>app.py</b></td>
        <td style='padding:8px;border:1px solid #161B22'>Sadece results.json okur, UI gösterir</td>
        <td style='padding:8px;border:1px solid #161B22'>streamlit run app.py</td></tr>
  </tbody>
</table>
<div class='warn-box' style='margin-top:20px'>
  ⚠️ <b>Yasal Uyarı:</b> Bu platform yalnızca bilgilendirme ve araştırma amaçlıdır.
  Üretilen sinyaller yatırım tavsiyesi niteliği taşımaz. Tüm yatırım kararları
  yatırımcının kendi sorumluluğundadır.
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
        asc  = sum(v["sc"])  / len(v["sc"])
        achg = sum(v["chg"]) / len(v["chg"])
        sec_rows.append({
            "Sektör":               k,
            "Ort. Master Skor":     int(asc),
            "Sektör Momentumu (%)": round(achg, 2),
            "Göreceli Güç (RS)":    round(asc * 0.6 + achg * 0.4, 2),
            "Hisseler":             ", ".join(v["h"]),
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
    render_news_tab()
