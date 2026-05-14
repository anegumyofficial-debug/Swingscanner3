import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Swing Trading Scanner", layout="wide")

# --- CUSTOM CSS (Agar tampilan bersih & profesional) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    div[data-testid="stMetricValue"] { font-size: 24px; }
    .status-up { color: green; font-weight: bold; }
    .status-down { color: red; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI SCANNER ---
@st.cache_data(ttl=3600)
def scan_saham(ticker_list):
    results = []
    for ticker in ticker_list:
        try:
            # Ambil data historis
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)
            if len(df) < 50: continue
            
            # Hitung Indikator (MA & RSI seperti di screenshot)
            df['MA20'] = ta.sma(df['Close'], length=20)
            df['MA50'] = ta.sma(df['Close'], length=50)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            last_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            change_pct = ((last_price - prev_price) / prev_price) * 100
            last_rsi = df['RSI'].iloc[-1]
            last_ma20 = df['MA20'].iloc[-1]
            last_ma50 = df['MA50'].iloc[-1]
            
            # Logika Trend
            trend = "Up-Trend" if last_price > last_ma50 else "Down-Trend"
            
            # Logika Sinyal (Actionable)
            if last_rsi < 35:
                action = "BUY (Oversold)"
            elif last_price > last_ma20 and prev_price <= df['MA20'].iloc[-2]:
                action = "BUY (MA Cross)"
            elif last_rsi > 70:
                action = "SELL (Overbought)"
            else:
                action = "Wait/Neutral"
            
            results.append({
                "Ticker": ticker.replace(".JK", ""),
                "Price": f"{last_price:,.0f}",
                "Change %": round(change_pct, 2),
                "RSI": round(last_rsi, 2),
                "Trend": trend,
                "Actionable": action
            })
        except:
            continue
    return pd.DataFrame(results)

# --- TAMPILAN UTAMA ---
st.title("📈 Swing Trading Scanner")

# Sidebar untuk filter seperti di screenshot
with st.sidebar:
    st.header("Filter Strategi")
    strategi = st.multiselect("Pilih Strategi:", 
                             ["MA 20 Cross", "MA 50 Cross", "RSI Oversold", "Price Action"],
                             default=["MA 20 Cross", "RSI Oversold"])
    min_rsi = st.slider("Min RSI", 0, 100, 30)
    
# Layout Tab (Scanner, Market Heatmap, Stock Analysis)
tab1, tab2, tab3 = st.tabs(["🔍 Scanner", "🔥 Market Heatmap", "📊 Stock Analysis"])

with tab1:
    st.subheader("Actionable Signals")
    
    # Load data dari CSV atau list
    try:
        tickers = pd.read_csv('saham_list.csv')['Ticker'].tolist()
    except:
        tickers = ["BBCA.JK", "BBRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK"]

    with st.spinner("Memindai pasar..."):
        df_scan = scan_saham(tickers)

    # Fungsi untuk mewarnai tabel
    def color_rows(val):
        if "BUY" in str(val): return 'background-color: #d4edda; color: #155724'
        if "SELL" in str(val): return 'background-color: #f8d7da; color: #721c24'
        if "Up-Trend" in str(val): return 'color: green'
        if "Down-Trend" in str(val): return 'color: red'
        return ''

    if not df_scan.empty:
        # Menampilkan tabel dengan gaya CSS
        st.dataframe(df_scan.style.applymap(color_rows, subset=['Actionable', 'Trend']), 
                     use_container_width=True, 
                     height=500)
    else:
        st.error("Data tidak ditemukan.")

with tab2:
    st.info("Fitur Market Heatmap akan menampilkan visualisasi performa sektor.")
    # Anda bisa menambahkan Plotly Treemap di sini

with tab3:
    st.info("Pilih saham di tabel untuk melihat grafik teknis mendalam.")

# --- FOOTER ---
st.markdown("---")
st.markdown("© 2024 **Duplicate Infeksius Actio** | Data source: Yahoo Finance")
