import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime, timedelta
import concurrent.futures

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Infectious Actio Clone", layout="wide")

# --- CUSTOM CSS (Agar Mirip Target) ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 8px; border: 1px solid #e0e0e0; }
    .buy-signal { color: green; font-weight: bold; }
    .sell-signal { color: red; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- DAFTAR SAHAM (DATABASE) ---
# Di website target, mereka melakukan scan ke hampir seluruh saham aktif (200-400 saham).
TICKERS = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "AMRT.JK", "BBNI.JK"] 

# --- LOGIKA ANALISIS (BACKEND) ---
def analyze_stock(ticker):
    try:
        # Ambil data lebih banyak (6 bulan) untuk akurasi MA & RSI
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 50: return None
        
        # Kalkulasi Indikator
        df['RSI'] = ta.rsi(df['Close'], length=14)
        bbands = ta.bbands(df['Close'], length=20, std=2)
        df = pd.concat([df, bbands], axis=1)
        df['MA20'] = ta.sma(df['Close'], length=20)
        
        # Ambil baris terakhir dengan cara yang aman (Fixing your previous error)
        latest = df.iloc[-1]
        price = float(latest['Close'])
        rsi_val = float(latest['RSI'])
        bbl = float(latest.iloc[:, 7]) # Kolom Lower Band
        bbu = float(latest.iloc[:, 9]) # Kolom Upper Band
        
        # --- LOGIKA SIGNAL ---
        signal = "HOLD"
        zone = "NEUTRAL"
        
        if price <= bbl or rsi_val < 35:
            signal = "BUY"
            zone = "OVERSOLD"
        elif price >= bbu or rsi_val > 70:
            signal = "SELL"
            zone = "OVERBOUGHT"
            
        return {
            "Ticker": ticker.replace(".JK", ""),
            "Price": f"{price:,.0f}",
            "Signal": signal,
            "Zone": zone,
            "RSI": f"{rsi_val:.2f}",
            "MA20": f"{latest['MA20']:,.0f}"
        }
    except:
        return None

# --- UI HEADER ---
st.title("📈 Infectious Actio - Swing Scanner V3")
st.info("Penyaring Saham Real-time Berdasarkan Teknikal Indikator (BB, RSI, SMA)")

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.header("⚙️ Filter Panel")
    min_rsi = st.slider("Min RSI", 0, 100, 30)
    max_rsi = st.slider("Max RSI", 0, 100, 70)
    start_scan = st.button("🚀 Mulai Pemindaian Database")

# --- PROSES SCANNING (MULTITHREADING) ---
if start_scan:
    st.subheader("🔍 Hasil Pemindaian")
    progress_bar = st.progress(0)
    
    results = []
    # Menggunakan ThreadPoolExecutor agar scan cepat (tidak satu-satu)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(analyze_stock, t): t for t in TICKERS}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_ticker)):
            res = future.result()
            if res: results.append(res)
            progress_bar.progress((i + 1) / len(TICKERS))

    if results:
        final_df = pd.DataFrame(results)
        
        # Tampilkan Tabel dengan Style
        def color_signal(val):
            color = 'green' if val == 'BUY' else 'red' if val == 'SELL' else 'black'
            return f'color: {color}; font-weight: bold'

        st.dataframe(final_df.style.applymap(color_signal, subset=['Signal']), width='stretch')
    else:
        st.warning("Tidak ada data yang ditemukan. Coba lagi nanti.")

else:
    st.write("Silakan klik tombol di sidebar untuk mulai memindai database saham.")
