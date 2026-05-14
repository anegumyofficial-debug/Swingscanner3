import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(layout="wide", page_title="Master Stock Scanner Pro")

# 2. CSS CUSTOM UNTUK TAMPILAN IDENTIK
st.markdown("""
    <style>
    /* Mengatur kotak Metric agar berbayang dan melengkung rapi */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 20px !important;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    /* Mempercantik font pada Metric */
    [data-testid="stMetricLabel"] { font-size: 15px !important; font-weight: 600 !important; color: #495057 !important; }
    [data-testid="stMetricValue"] { font-size: 26px !important; font-weight: 700 !important; color: #212529 !important; }
    
    /* Tabel agar lebih luas dan rapi */
    .stDataFrame { border-radius: 12px; overflow: hidden; border: 1px solid #e9ecef; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Master Stock Scanner - Pro Dashboard")
st.write(f"Update: {datetime.now().strftime('%A, %d %B %Y | %H:%M')} WIB")
st.markdown("---")

# 3. DAFTAR SAHAM
tickers = ["BBRI.JK", "BBCA.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "BMRI.JK"]

# 4. LOGIKA ANALISIS (Selalu ambil data terakhir yang valid)
def fetch_stock_data(ticker, timeframe):
    config = {
        "Day (Scalping)": {"p": "1mo", "i": "1h", "rsi_l": 30},
        "Weekly (Swing)": {"p": "6mo", "i": "1d", "rsi_l": 40},
        "Monthly (Invest)": {"p": "2y", "i": "1wk", "rsi_l": 45}
    }
    c = config[timeframe]
    df = yf.download(ticker, period=c['p'], interval=c['i'], progress=False, auto_adjust=True)
    
    if df is None or df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

    # Indikator
    df['RSI'] = ta.rsi(df['Close'], length=14)
    bb = ta.bbands(df['Close'], length=20, std=2)
    df = pd.concat([df, bb], axis=1).dropna(subset=['Close', 'RSI'])
    
    # Ambil baris terakhir yang ada datanya
    last = df.iloc[-1]
    price = round(float(last['Close']), 0)
    rsi_v = round(float(last['RSI']), 2)
    l_band = round(float(last.filter(like='BBL').iloc), 0)
    u_band = round(float(last.filter(like='BBU').iloc), 0)

    # Logika Status
    if rsi_v <= c['rsi_l'] or price <= l_band:
        status, signal = "🟢 SIAP SEROK", "buy"
    elif rsi_v >= (100 - c['rsi_l']) or price >= u_band:
        status, signal = "🔴 JUAL / PROFIT", "sell"
    else:
        status, signal = "⚪ WAIT / NEUTRAL", "neutral"

    return {"Saham": ticker.replace(".JK", ""), "Harga": price, "Status": status, "RSI": rsi_v, "sig": signal}

# 5. RENDER DASHBOARD (BAR METRIC & TABEL)
tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

def render_view(tab, label):
    with tab:
        data_rows = []
        for t in tickers:
            res = fetch_stock_data(t, label)
            if res: data_rows.append(res)
        
        if data_rows:
            df_final = pd.DataFrame(data_rows)
            
            # --- BAR METRIC (IDENTIK REFERENSI) ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Pantauan", len(tickers))
            m2.metric("Siap Serok", len(df_final[df_final['sig'] == 'buy']))
            m3.metric("Waktunya Jual", len(df_final[df_final['sig'] == 'sell']))
            m4.metric("Posisi Wait", len(df_final[df_final['sig'] == 'neutral']))
            
            st.markdown("### 📊 Detail Analisis Terupdate")
            
            # Styling Warna Status
            def color_status(v):
                if "SEROK" in str(v): return 'background-color: #d4edda; color: #155724; font-weight: bold'
                if "JUAL" in str(v): return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                return ''

            st.dataframe(
                df_final.drop(columns=['sig']).style.applymap(color_status, subset=['Status']),
                use_container_width=True
            )

render_view(tab1, "Day (Scalping)")
render_view(tab2, "Weekly (Swing)")
render_view(tab3, "Monthly (Invest)")
