import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from datetime import datetime

# 1. KONFIGURASI LAYOUT
st.set_page_config(layout="wide", page_title="Master Stock Scanner Pro")

# 2. CSS CUSTOM (IDENTIK DENGAN REFERENSI)
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px 20px !important;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .stDataFrame { border: 1px solid #e0e0e0; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Master Stock Scanner - Pro Dashboard")
st.write(f"Update: {datetime.now().strftime('%d %B %Y | %H:%M')} WIB")
st.markdown("---")

# 3. LOGIKA ANALISIS (Selalu ambil nilai terupdate)
def fetch_data(ticker, label):
    config = {
        "Day (Scalping)": {"p": "1mo", "i": "1h", "rsi_l": 30},
        "Weekly (Swing)": {"p": "6mo", "i": "1d", "rsi_l": 40},
        "Monthly (Invest)": {"p": "2y", "i": "1wk", "rsi_l": 45}
    }
    c = config[label]
    df = yf.download(ticker, period=c['p'], interval=c['i'], progress=False, auto_adjust=True)
    
    if df is None or df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

    df['RSI'] = ta.rsi(df['Close'], length=14)
    bb = ta.bbands(df['Close'], length=20, std=2)
    df = pd.concat([df, bb], axis=1).dropna(subset=['Close', 'RSI'])
    
    # Ambil baris terakhir yang valid
    latest = df.iloc[-1]
    price = round(float(latest['Close']), 0)
    rsi_v = round(float(latest['RSI']), 2)
    l_band = round(float(latest.filter(like='BBL').iloc), 0)
    
    if rsi_v <= c['rsi_l'] or price <= l_band:
        status, sig = "🟢 SIAP SEROK", "buy"
    else:
        status, sig = "⚪ WAIT / NEUTRAL", "neutral"

    return {"Saham": ticker.replace(".JK", ""), "Harga": price, "Status": status, "RSI": rsi_v, "sig": sig}

# 4. IMPLEMENTASI BAR METRIC & TABEL
tickers = ["BBRI.JK", "BBCA.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "BMRI.JK"]
tabs = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

for tab, label in zip(tabs, ["Day (Scalping)", "Weekly (Swing)", "Monthly (Invest)"]):
    with tab:
        results = []
        for t in tickers:
            try:
                res = fetch_data(t, label)
                if res: results.append(res)
            except: continue
        
        if results:
            df_res = pd.DataFrame(results)
            # --- BAR METRIC (SUMMARY) ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Pantauan", len(tickers))
            m2.metric("🟢 Siap Serok", len(df_res[df_res['sig'] == 'buy']))
            m3.metric("⚪ Neutral", len(df_res[df_res['sig'] == 'neutral']))
            
            st.markdown("### Detail Analisis Terupdate")
            st.dataframe(df_res.drop(columns=['sig']), use_container_width=True)
