import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import plotly.graph_objects as go

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Swing Trading Scanner", layout="wide")

# --- CSS CUSTOM UNTUK TAMPILAN ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & SIDEBAR ---
st.title("📈 Swing Trading Scanner V.2")
st.caption("Realtime Daily Market Screening • Indonesia Stock Exchange")

with st.sidebar:
    st.header("📊 • INFECTIOUS ACTIO")
    st.subheader("🧩 Panel Kontrol Utama")
    tp_input = st.number_input("Take Profit (%)", value=5)
    sl_input = st.number_input("Stop Loss (%)", value=3)
    filter_fake = st.checkbox("Filter Fake Rebound")
    
    st.subheader("📋 Pilih Menu")
    menu = st.selectbox("Menu", ["Screener Saham", "Harga Wajar", "Average Down"])
    
    search_code = st.text_input("🔍 Cari Kode Saham (Contoh: BBCA.JK)")

# --- RINGKASAN PASAR (IHSG) ---
st.subheader("📈 IHSG Daily (TradingView Style)")
col1, col2, col3, col4 = st.columns(4)

# Simulasi data IHSG (Ganti dengan API Saham jika ada)
ihsg_val = 7585.69
ihsg_change = -1.62

col1.metric("IHSG", f"{ihsg_val}", f"{ihsg_change}%", delta_color="inverse")
col2.write(f"**📅 Harga Hari Ini:** {datetime.date.today()}")

# --- TABEL SIGNAL (FILTER STRATEGI) ---
st.subheader("🎯 FILTER STRATEGI")

# Contoh Data Frame untuk Tabel
data = {
    "Kode": ["BJTM", "BMHS", "MTWI", "JGLE", "BNGA"],
    "Harga": [575.0, 193.0, 358.0, 55.0, 1770.0],
    "Signal": ["HOLD", "HOLD", "HOLD", "HOLD", "BUY"],
    "Trend": ["🟢 Bullish", "🟢 Bullish", "🔴 Bearish", "🟢 Bullish", "🟢 Bullish"],
    "Zone": ["SELL", "MID", "MID", "MID", "BUY"],
    "MA": ["MA5, MA50", "MA10, MA100", "MA20", "MA50", "None"],
    "RSI": [50.2, 51.4, 51.8, 53.0, 32.5]
}

df = pd.DataFrame(data)

# Tampilkan Tabel
st.dataframe(df, use_container_width=True)

# --- FUNGSI ANALISIS SEDERHANA ---
if search_code:
    st.write(f"### Analisis Untuk {search_code}")
    try:
        # Mengambil data saham dari Yahoo Finance
        ticker = yf.Ticker(search_code)
        hist = ticker.history(period="1mo")
        
        # Membuat Grafik Candlestick
        fig = go.Figure(data=[go.Candlestick(x=hist.index,
                        open=hist['Open'], high=hist['High'],
                        low=hist['Low'], close=hist['Close'])])
        fig.update_layout(title=f"Chart {search_code}", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Gagal mengambil data untuk {search_code}. Pastikan format benar (contoh: ASII.JK)")

st.info("Update otomatis harian • Last update: " + datetime.datetime.now().strftime("%d %b %Y %H:%M"))
