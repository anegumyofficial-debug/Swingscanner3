import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from datetime import datetime

# 1. SETTING HALAMAN (LAYOUT LEBAR)
st.set_page_config(layout="wide", page_title="Master Stock Scanner Pro")

# 2. CSS CUSTOM AGAR IDENTIK DENGAN REFERENSI
st.markdown("""
    <style>
    /* Styling Kotak Metric (Bar Summary) */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px 20px !important;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    /* Memperluas area tabel */
    .stDataFrame { border: 1px solid #e0e0e0; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Master Stock Scanner - Pro Dashboard")
st.write(f"Kondisi Pasar Terakhir: {datetime.now().strftime('%d %B %Y | %H:%M')} WIB")
st.markdown("---")

# 3. DAFTAR SAHAM
tickers = ["BBRI.JK", "BBCA.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "BMRI.JK"]

# 4. LOGIKA ANALISIS (Selalu ambil nilai terupdate)
def fetch_and_analyze(ticker, label):
    config = {
        "Day (Scalping)": {"p": "1mo", "i": "1h", "rsi_l": 30},
        "Weekly (Swing)": {"p": "6mo", "i": "1d", "rsi_l": 40},
        "Monthly (Invest)": {"p": "2y", "i": "1wk", "rsi_l": 45}
    }
    c = config[label]
    df = yf.download(ticker, period=c['p'], interval=c['i'], progress=False, auto_adjust=True)
    
    if df is None or df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

    # Indikator
    df['RSI'] = ta.rsi(df['Close'], length=14)
    bb = ta.bbands(df['Close'], length=20, std=2)
    df = pd.concat([df, bb], axis=1).dropna(subset=['Close', 'RSI'])
    
    # Ambil baris terakhir (Meskipun IHSG tutup tetap muncul harga terakhir)
    latest = df.iloc[-1]
    price = round(float(latest['Close']), 0)
    rsi_val = round(float(latest['RSI']), 2)
    l_band = round(float(latest.filter(like='BBL').iloc), 0)
    u_band = round(float(latest.filter(like='BBU').iloc), 0)

    # Logika Sinyal
    if rsi_val <= c['rsi_l'] or price <= l_band:
        status, sig = "🟢 SIAP SEROK", "buy"
    elif rsi_val >= (100 - c['rsi_l']) or price >= u_band:
        status, sig = "🔴 JUAL / PROFIT", "sell"
    else:
        status, sig = "⚪ WAIT / NEUTRAL", "neutral"

    return {"Saham": ticker.replace(".JK", ""), "Harga": price, "Status": status, "RSI": rsi_val, "sig": sig}

# 5. TAMPILAN BAR METRIC & TABEL
tabs = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

for tab, label in zip(tabs, ["Day (Scalping)", "Weekly (Swing)", "Monthly (Invest)"]):
    with tab:
        results = []
        for t in tickers:
            data = fetch_and_analyze(t, label)
            if data: results.append(data)
        
        if results:
            df_final = pd.DataFrame(results)
            
            # --- BAR SUMMARY (IDENTIK REFERENSI) ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Pantauan", len(tickers))
            m2.metric("Siap Serok", len(df_final[df_final['sig'] == 'buy']))
            m3.metric("Waktunya Jual", len(df_final[df_final['sig'] == 'sell']))
            m4.metric("Posisi Wait", len(df_final[df_final['sig'] == 'neutral']))
            
            st.markdown("### 📋 Detail Analisis")
            
            # Warna Baris
            def color_status(v):
                if "SEROK" in str(v): return 'background-color: #d4edda; color: #155724; font-weight: bold'
                if "JUAL" in str(v): return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                return ''

            st.dataframe(df_final.drop(columns=['sig']).style.applymap(color_status, subset=['Status']), use_container_width=True)
