# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════════════════╗
# ║   BİST ULTIMATE QUANT TERMINAL v1.0 — MOTOR (ARKA PLAN İŞÇİSİ)    ║
# ║   Çalıştır: python motor.py                                         ║
# ║   Çıktı   : ~/bist_cache/results.json  (app.py tarafından okunur)  ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
# Bu dosya, tüm ağır işleri (veri çekme, indikatör hesaplama, AI eğitimi
# ve analiz) yapar ve sonuçları bir JSON dosyasına kaydeder.
# Streamlit arayüzü (app.py) bu JSON'u okuyarak anında açılır.
#
# Kullanım:
#   python motor.py              → tüm hisseleri analiz et, kaydet
#   python motor.py --ai         → Ensemble AI motoruyla çalıştır
#   python motor.py --trend NEG  → Endeks yönünü NEGATİF olarak ayarla
#
# Cron / Zamanlanmış görev örneği (her saat başı):
#   0 * * * * cd /app && python motor.py --ai >> /tmp/motor.log 2>&1

import os
import sys
import json
import time
import random
import argparse
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

# ── curl_cffi (opsiyonel) ──
try:
    from curl_cffi import requests as cffi_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    import requests as cffi_requests
    CURL_CFFI_AVAILABLE = False

# ── ML kütüphaneleri (opsiyonel) ──
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.calibration import CalibratedClassifierCV
    import xgboost as xgb
    import lightgbm as lgb
    from catboost import CatBoostClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────
# AYARLAR
# ─────────────────────────────────────────────────────────────────────
CACHE_DIR           = os.path.join(os.environ.get("HOME", "/tmp"), "bist_cache")
CACHE_STALE_SECONDS = 3600
RESULTS_FILE        = os.path.join(CACHE_DIR, "results.json")
os.makedirs(CACHE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finance.yahoo.com/",
}

RANGE_MAP    = {"1y": "1y", "2y": "2y", "3m": "3m", "6m": "6m", "1mo": "1mo", "60d": "60d"}
INTERVAL_MAP = {"1d": "1d", "1h": "1h", "1wk": "1wk"}

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

FEATURE_COLS = [
    "RSI", "Fisher_RSI", "MACD_Hist", "BB_BW", "Squeeze",
    "Stoch_K", "Stoch_D", "OBV_Slope", "OBV_Breakout",
    "Vol_Anomaly", "Vol_Spike", "Smart_Money", "MFI", "LogRetVol",
    "ATR",
]


# ─────────────────────────────────────────────────────────────────────
# VERİ ÇEKME
# ─────────────────────────────────────────────────────────────────────
def fetch_yahoo_chart(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
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
        if resp.status_code != 200:
            return pd.DataFrame()
        data   = resp.json()
        result = data.get("chart", {}).get("result", [])
        if not result or result[0] is None:
            return pd.DataFrame()
        chart      = result[0]
        timestamps = chart.get("timestamp", [])
        if not timestamps:
            return pd.DataFrame()
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
    return os.path.join(
        CACHE_DIR,
        f"{sym.replace('.IS','').replace('=X','usd').lower()}_{period}_{interval}.json"
    )


def fetch_market_data(sym: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
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
            if not df.empty:
                return df
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
        if resp.status_code != 200:
            return {}
        data   = resp.json()
        result = data.get("quoteSummary", {}).get("result", [])
        if not result:
            return {}
        merged = {}
        for module in result[0].values():
            if isinstance(module, dict):
                merged.update(module)
        return {k: (v.get("raw") if isinstance(v, dict) else v) for k, v in merged.items()}
    except Exception:
        return {}


def fetch_fundamentals(sym: str) -> dict:
    cache_p = os.path.join(CACHE_DIR, f"fund_{sym.replace('.IS','').lower()}.json")
    now = time.time()
    if os.path.exists(cache_p) and (now - os.path.getmtime(cache_p)) < 21600:
        try:
            with open(cache_p, "r") as f:
                return json.load(f)
        except Exception:
            pass
    info = _fetch_ticker_info(sym)
    result = {
        "fk":   float(info.get("trailingPE") or info.get("forwardPE") or 10.0),
        "pddd": float(info.get("priceToBook") or 2.0),
        "beta": float(info.get("beta") or 1.0),
        "peg":  float(info.get("pegRatio") or 1.0),
        "roe":  float(info.get("returnOnEquity") or 0.15) * 100,
        "debt": float(info.get("debtToEquity") or 100.0),
    }
    try:
        with open(cache_p, "w") as f:
            json.dump(result, f)
    except Exception:
        pass
    return result


# ─────────────────────────────────────────────────────────────────────
# İNDİKATÖRLER
# ─────────────────────────────────────────────────────────────────────
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["EMA9"]  = df["Close"].ewm(span=9,  adjust=False).mean()
    df["EMA21"] = df["Close"].ewm(span=21, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["MA5"]   = df["Close"].rolling(5).mean()
    df["MA22"]  = df["Close"].rolling(22).mean()
    delta = df["Close"].diff()
    gain  = delta.where(delta > 0, 0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + gain / (loss + 1e-9) + 1e-9))
    rsi_s = (0.1 * (df["RSI"] - 50)).clip(-0.999, 0.999)
    df["Fisher_RSI"] = 0.5 * np.log((1 + rsi_s) / (1 - rsi_s + 1e-9))
    e12 = df["Close"].ewm(span=12, adjust=False).mean()
    e26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"]        = e12 - e26
    df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"]   = df["MACD"] - df["Signal_Line"]
    df["BB_Middle"] = df["Close"].rolling(20).mean()
    std = df["Close"].rolling(20).std()
    df["BB_Upper"]  = df["BB_Middle"] + 2 * std
    df["BB_Lower"]  = df["BB_Middle"] - 2 * std
    df["BB_BW"]     = (df["BB_Upper"] - df["BB_Lower"]) / (df["BB_Middle"] + 1e-9)
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift()).abs(),
        (df["Low"]  - df["Close"].shift()).abs(),
    ], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()
    df["KC_Upper"] = df["BB_Middle"] + 1.5 * df["ATR"]
    df["KC_Lower"] = df["BB_Middle"] - 1.5 * df["ATR"]
    df["Squeeze"]  = ((df["BB_Upper"] < df["KC_Upper"]) &
                      (df["BB_Lower"] > df["KC_Lower"])).astype(int)
    l14 = df["Low"].rolling(14).min()
    h14 = df["High"].rolling(14).max()
    df["Stoch_K"] = 100 * (df["Close"] - l14) / (h14 - l14 + 1e-9)
    df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()
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
    df["Vol_MA20"]    = df["Volume"].rolling(20).mean()
    df["Vol_Anomaly"] = df["Volume"] / (df["Vol_MA20"] + 1e-9)
    df["Vol_Spike"]   = (df["Vol_Anomaly"] >= 1.5).astype(int)
    clv = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / ((df["High"] - df["Low"]) + 1e-9)
    df["Smart_Money"] = np.where((df["Vol_Anomaly"] > 1.2) & (clv > 0.2), 1,
                        np.where((df["Vol_Anomaly"] > 1.2) & (clv < -0.2), -1, 0))
    tp  = (df["High"] + df["Low"] + df["Close"]) / 3.0
    rmf = tp * df["Volume"]
    pdir = np.where(tp > tp.shift(1), 1, -1)
    pos_f = pd.Series(np.where(pdir == 1, rmf, 0), index=df.index).rolling(14).sum()
    neg_f = pd.Series(np.where(pdir == -1, rmf, 0), index=df.index).rolling(14).sum()
    df["MFI"] = 100 - (100 / (1 + pos_f / (neg_f + 1e-9)))
    df["LogRetVol"] = np.log(df["Close"] / df["Close"].shift(1)).rolling(10).std()
    return df


# ─────────────────────────────────────────────────────────────────────
# REJİM
# ─────────────────────────────────────────────────────────────────────
def detect_regime_hisse(df: pd.DataFrame) -> str:
    if len(df) < 20:
        return "SIDEWAYS"
    c       = df.iloc[-1]
    atr_s   = df["ATR"].tail(30)
    atr_pct = (c["ATR"] - atr_s.min()) / (atr_s.max() - atr_s.min() + 1e-9) * 100
    slope   = ((df["EMA21"].tail(5).iloc[-1] - df["EMA21"].tail(5).iloc[0])
               / (df["EMA21"].tail(5).iloc[0] + 1e-9) * 100)
    pos     = ((c["Close"] - df["Low"].tail(10).min())
               / (df["High"].tail(10).max() - df["Low"].tail(10).min() + 1e-9) * 100)
    if   pos < 15 and atr_pct > 75 and slope < -0.5:
        return "PANIC"
    elif atr_pct > 80:
        return "HIGH_VOL"
    elif abs(slope) > 0.2:
        return "TRENDING"
    return "SIDEWAYS"


# ─────────────────────────────────────────────────────────────────────
# AI
# ─────────────────────────────────────────────────────────────────────
def build_target(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    past_max = df["Close"].rolling(5).max()
    df["TARGET"] = (past_max >= df["Close"].shift(4) * 1.05).astype(int)
    return df.dropna(subset=["TARGET"])


def train_ensemble(df: pd.DataFrame):
    if not SKLEARN_AVAILABLE or len(df) < 120:
        return None
    X = df[FEATURE_COLS].copy().fillna(0)
    y = df["TARGET"]
    n      = len(df)
    tr_end = int(n * 0.70)
    va_end = int(n * 0.85)
    X_tr, y_tr = X.iloc[:tr_end],       y.iloc[:tr_end]
    X_va, y_va = X.iloc[tr_end:va_end], y.iloc[tr_end:va_end]
    if len(X_tr) < 60 or len(X_va) < 15:
        return None
    models = {}
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
# SKOR & ANALİZ
# ─────────────────────────────────────────────────────────────────────
def kelly_position(prob: float, win_mult: float = 1.5, lose_mult: float = 1.0,
                   max_fraction: float = 0.25) -> float:
    q = 1 - prob
    k = (prob * win_mult - q * lose_mult) / (win_mult + 1e-9)
    return float(max(0.0, min(max_fraction, k)))


def atr_position(capital: float, entry: float, atr: float, risk_pct: float = 0.01) -> float:
    risk_tl = capital * risk_pct
    stop    = 2.0 * atr
    return risk_tl / (stop + 1e-9)


def calculate_master_score(df: pd.DataFrame, ai_prob: float,
                            index_trend: str, regime: str, fund: dict) -> dict:
    if len(df) < 5:
        return {"master": 50, "signal": "TUT", "ai": 50, "tech": 50, "fund_s": 50, "smart": 50}
    c  = df.iloc[-1]
    p  = df.iloc[-2]
    ai_s = int(ai_prob * 100)
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
    fk_s   = 70 if fund["fk"]   < 10 else (50 if fund["fk"]   < 18 else 30)
    pddd_s = 70 if fund["pddd"] < 1.5 else (50 if fund["pddd"] < 3  else 30)
    roe_s  = 70 if fund["roe"]  > 20  else (50 if fund["roe"]  > 10 else 30)
    fund_s = int((fk_s + pddd_s + roe_s) / 3)
    smart_s = 50
    smart_s += 20 if c.get("Smart_Money", 0) == 1 else (-20 if c.get("Smart_Money", 0) == -1 else 0)
    smart_s += 15 if c.get("OBV_Breakout", 0) == 1 else 0
    smart_s += 15 if c.get("Vol_Spike", 0) == 1 and c["Close"] > p["Close"] else 0
    smart_s += 10 if c.get("MFI", 50) < 25 else (-10 if c.get("MFI", 50) > 75 else 0)
    smart_s += 10 if c.get("Squeeze", 0) == 0 else -5
    smart_s = max(0, min(100, int(smart_s)))
    master = int(ai_s * 0.30 + tech_s * 0.35 + fund_s * 0.15 + smar
