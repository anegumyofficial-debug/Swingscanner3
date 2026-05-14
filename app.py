import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(layout="wide", page_title="Master Stock Scanner Pro")

# 2. CSS UNTUK TAMPILAN IDENTIK (Metric Bar & Tabel)
st.markdown("""
    <style>
    /* Mengatur gaya kotak Metric agar sama persis dengan referensi */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 20px !important;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    /* Mengatur font agar lebih modern */
    [data-testid="stMetricLabel"] { font-size: 16px !important; font-weight: 600 !important; color: #6c757d !important; }
    [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700 !important; }
    
    /* Memperluas area tabel agar memenuhi layar */
    .stDataFrame { border: 1px solid #dee2e6; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Master Stock Scanner - Pro Dashboard")
st.write(f"Kondisi Pasar: {datetime.now().strftime('%A, %d %B %Y | %H:%M')} WIB")
st.markdown("---")

# 3. DAFTAR SAHAM
tickers = ["BBRI.JK", "BBCA.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "BMRI.JK"]

# 4. LOGIKA ANALISIS (Selalu ambil data valid terakhir)
def analyze_stock(ticker, timeframe):
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
    
    # Ambil baris terakhir yang memiliki data (Anti-IHSG Tutup)
    last = df.iloc[-1]
    price = round(float(last['Close']), 0)
    rsi_v = round(float(last['RSI']), 2)
    l_band = round(float(last.filter(like='BBL').iloc), 0)
    u_band = round(float(last.filter(like='BBU').iloc), 0)

    # Logika Status
    if rsi_v <= c['rsi_l'] or price <= l_band:
        status, sig = "🟢 SIAP SEROK", "buy"
    elif rsi_v >= (100 - c['rsi_l']) or price >= u_band:
        status, sig = "🔴 JUAL / PROFIT", "sell"
    else:
        status, sig = "⚪ WAIT / NEUTRAL", "neutral"

    return {"Saham": ticker.replace(".JK", ""), "Harga": price, "Status": status, "RSI": rsi_v, "sig": sig}

# 5. RENDER DASHBOARD (Metric Bar Baru & Tabel)
tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

def render_content(tab, label):
    with tab:
        results = []
        for t in tickers:
            data = analyze_stock(t, label)
            if data: results.append(data)
        
        if results:
            df_final = pd.DataFrame(results)
            
            # --- BAR BARU (SUMMARY METRICS) ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Pantauan", f"{len(tickers)}")
            m2.metric("Siap Serok", len(df_final[df_final['sig'] == 'buy']))
            m3.metric("Waktunya Jual", len(df_final[df_final['sig'] == 'sell']))
            m4.metric("Posisi Wait", len(df_final[df_final['sig'] == 'neutral']))
            
            st.markdown("### 📋 Detail Rekomendasi Terupdate")
            
            # Pewarnaan Baris
            def color_row(v):
                if "SEROK" in str(v): return 'background-color: #d4edda; color: #155724; font-weight: bold'
                if "JUAL" in str(v): return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                return ''

            st.dataframe(
                df_final.drop(columns=['sig']).style.applymap(color_row, subset=['Status']),
                use_container_width=True
            )

render_content(tab1, "Day (Scalping)")
render_content(tab2, "Weekly (Swing)")
render_content(tab3, "Monthly (Invest)")
