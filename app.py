import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(layout="wide", page_title="Master Stock Scanner Pro v3.0")

# Custom CSS untuk Bar Metrics
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Master Stock Scanner - Terupdate")
st.write(f"Waktu Sistem: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB")

# 2. DAFTAR SAHAM
tickers = ["BBRI.JK", "BBCA.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "BMRI.JK"]

# 3. FUNGSI ANALISIS TERUPDATE
def fetch_and_analyze(ticker, timeframe_label):
    config = {
        "Day (Scalping)": {"period": "1mo", "interval": "1h", "tp": 0.02, "sl": 0.015, "rsi_low": 30},
        "Weekly (Swing)": {"period": "6mo", "interval": "1d", "tp": 0.07, "sl": 0.04, "rsi_low": 40},
        "Monthly (Invest)": {"period": "2y", "interval": "1wk", "tp": 0.15, "sl": 0.07, "rsi_low": 45}
    }
    
    conf = config[timeframe_label]
    df = yf.download(ticker, period=conf['period'], interval=conf['interval'], progress=False, auto_adjust=True)
    
    if df is None or df.empty:
        return None
        
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Indikator
    df['RSI'] = ta.rsi(df['Close'], length=14)
    bbands = ta.bbands(df['Close'], length=20, std=2)
    
    if bbands is None: return None
    df = pd.concat([df, bbands], axis=1)
    
    # LOGIKA UPDATE: Ambil baris terakhir yang benar-benar ada harganya (Bukan NaN)
    df_valid = df.dropna(subset=['Close', 'RSI'])
    if df_valid.empty: return None
    latest = df_valid.iloc[-1]
    
    col_bbl = [c for c in df_valid.columns if 'BBL' in c]
    col_bbu = [c for c in df_valid.columns if 'BBU' in c]
    
    price = float(latest['Close'])
    rsi_val = float(latest['RSI'])
    l_band = float(latest[col_bbl])
    u_band = float(latest[col_bbu])

    if rsi_val <= conf['rsi_low'] or price <= l_band:
        status, lbl = "🟢 SIAP SEROK", "buy"
        entry, tp, sl = price, round(price * (1 + conf['tp']), 0), round(price * (1 - conf['sl']), 0)
    elif rsi_val >= (100 - conf['rsi_low']) or price >= u_band:
        status, lbl = "🔴 JUAL / PROFIT", "sell"
        entry, tp, sl = "-", "AMBIL PROFIT", "-"
    else:
        status, lbl = "⚪ WAIT", "neutral"
        entry, tp, sl = round(l_band, 0), round(u_band, 0), round(l_band * (1 - conf['sl']), 0)

    return {"Saham": ticker.replace(".JK", ""), "Harga": round(price, 0), "Status": status, 
            "Entry": entry, "TP": tp, "SL": sl, "RSI": round(rsi_val, 2), "lbl": lbl}

# 4. TAMPILAN DASHBOARD
def style_status(val):
    if "SIAP SEROK" in str(val): return 'background-color: #d4edda; color: #155724; font-weight: bold'
    if "JUAL" in str(val): return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
    return ''

tabs = st.tabs(["🕒 Scalping", "📅 Swing", "🏛️ Invest"])

for tab, label in zip(tabs, ["Day (Scalping)", "Weekly (Swing)", "Monthly (Invest)"]):
    with tab:
        results = []
        for t in tickers:
            try:
                data = fetch_and_analyze(t, label)
                if data: results.append(data)
            except: continue
        
        if results:
            df = pd.DataFrame(results)
            # BAR METRICS (Summary Baru)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total", len(tickers))
            m2.metric("Buy", len(df[df['lbl'] == 'buy']))
            m3.metric("Sell", len(df[df['lbl'] == 'sell']))
            m4.metric("Wait", len(df[df['lbl'] == 'neutral']))
            
            # TABEL
            st.dataframe(df.drop(columns=['lbl']).style.applymap(style_status, subset=['Status']), use_container_width=True)
        else:
            st.warning("Menghubungkan ke database bursa...")
