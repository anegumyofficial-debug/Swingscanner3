import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from datetime import datetime

# 1. SETTING HALAMAN (WAJIB LEBAR)
st.set_page_config(layout="wide", page_title="Master Stock Scanner Pro")

# 2. CSS CUSTOM (Ini kunci agar tampilan kotak/bar metrik sama persis)
st.markdown("""
    <style>
    /* Mengubah latar belakang utama */
    .main { background-color: #f8f9fa; }
    
    /* Mempercantik kotak Metrik (Bar Baru) */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Mengatur header tabel agar lebih bersih */
    .stDataFrame { border: 1px solid #e0e0e0; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Master Stock Scanner - Pro Dashboard")
st.write(f"Kondisi Pasar Terakhir: {datetime.now().strftime('%d %M %Y %H:%M')} WIB")
st.markdown("---")

# 3. LOGIKA ANALISIS TERUPDATE (Tetap muncul meski IHSG tutup)
def fetch_stock_data(ticker, label):
    config = {
        "Day (Scalping)": {"period": "1mo", "interval": "1h", "rsi_low": 30},
        "Weekly (Swing)": {"period": "6mo", "interval": "1d", "rsi_low": 40},
        "Monthly (Invest)": {"period": "2y", "interval": "1wk", "rsi_low": 45}
    }
    conf = config[label]
    df = yf.download(ticker, period=conf['period'], interval=conf['interval'], progress=False, auto_adjust=True)
    
    if df is None or df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

    # Indikator
    df['RSI'] = ta.rsi(df['Close'], length=14)
    bb = ta.bbands(df['Close'], length=20, std=2)
    df = pd.concat([df, bb], axis=1).dropna(subset=['Close', 'RSI'])
    
    # Ambil baris terakhir yang valid (Logika Nilai Terupdate)
    latest = df.iloc[-1]
    price = round(float(latest['Close']), 0)
    rsi_val = round(float(latest['RSI']), 2)
    l_band = round(float(latest.filter(like='BBL').iloc), 0)
    u_band = round(float(latest.filter(like='BBU').iloc), 0)

    # Penentuan Status
    if rsi_val <= conf['rsi_low'] or price <= l_band:
        status, color = "🟢 SIAP SEROK", "buy"
    elif rsi_val >= (100 - conf['rsi_low']) or price >= u_band:
        status, color = "🔴 JUAL / PROFIT", "sell"
    else:
        status, color = "⚪ WAIT / NEUTRAL", "neutral"

    return {"Saham": ticker.replace(".JK", ""), "Harga": price, "Status": status, "RSI": rsi_val, "color": color}

# 4. IMPLEMENTASI BAR METRIK & TABEL
tickers = ["BBRI.JK", "BBCA.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "BMRI.JK"]
tabs = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

for tab, label in zip(tabs, ["Day (Scalping)", "Weekly (Swing)", "Monthly (Invest)"]):
    with tab:
        results = []
        for t in tickers:
            data = fetch_stock_data(t, label)
            if data: results.append(data)
        
        if results:
            df_res = pd.DataFrame(results)
            
            # --- BAR BARU (SAMA DENGAN REFERENSI) ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Saham", len(tickers))
            col2.metric("Siap Serok", len(df_res[df_res['color'] == 'buy']))
            col3.metric("Waktunya Jual", len(df_res[df_res['color'] == 'sell']))
            col4.metric("Posisi Wait", len(df_res[df_res['color'] == 'neutral']))
            
            st.markdown("### Detail Sinyal Saham")
            
            # Fungsi Pewarnaan Baris Tabel
            def color_status(val):
                if "SEROK" in str(val): return 'background-color: #d4edda; color: #155724; font-weight: bold'
                if "JUAL" in str(val): return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                return ''

            st.dataframe(
                df_res.drop(columns=['color']).style.applymap(color_status, subset=['Status']),
                use_container_width=True
            )
