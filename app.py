import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

# Konfigurasi Halaman (Agar mirip dengan aslinya)
st.set_page_config(page_title="Swing Trading Scanner", layout="wide")

st.title("📈 Swing Trading Scanner - Infeksius Actio")
st.markdown("---")

# 1. Sidebar untuk Filter
st.sidebar.header("Filter Strategi")
rsi_threshold = st.sidebar.slider("RSI Threshold", 0, 100, 30)
ma_period = st.sidebar.selectbox("Moving Average Period",)

# 2. Daftar Saham (Contoh beberapa ticker)
tickers = ["BBCA.JK", "BBRI.JK", "ASII.JK", "TLKM.JK", "GOTO.JK"]

@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, period="1y", interval="1d")
    # Menghitung Indikator Teknis
    data['RSI'] = ta.rsi(data['Close'], length=14)
    data['MA'] = ta.sma(data['Close'], length=ma_period)
    return data

# 3. Logika Scanner
scanner_results = []

for t in tickers:
    df = load_data(t)
    last_row = df.iloc[-1]
    
    # Contoh Kondisi Strategi: RSI di bawah threshold (Oversold)
    if last_row['RSI'] < rsi_threshold:
        scanner_results.append({
            "Ticker": t,
            "Price": last_row['Close'],
            "RSI": round(last_row['RSI'], 2),
            "MA": round(last_row['MA'], 2),
            "Signal": "BUY / OVERSOLD"
        })

# 4. Menampilkan Hasil di Website
if scanner_results:
    df_result = pd.DataFrame(scanner_results)
    st.write(f"### Ditemukan {len(df_result)} Saham Berdasarkan Filter")
    st.table(df_result) # Atau st.dataframe(df_result) untuk tabel interaktif
else:
    st.warning("Tidak ada saham yang memenuhi kriteria saat ini.")

# 5. Grafik Detail (Opsional)
st.subheader("Detail Grafik")
selected_stock = st.selectbox("Pilih Saham untuk Dilihat:", tickers)
chart_data = load_data(selected_stock)
st.line_chart(chart_data[['Close', 'MA']])
