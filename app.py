import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Swing Trading Scanner", layout="wide")

# --- STYLE CSS AGAR MIRIP ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (FILTER STRATEGI) ---
with st.sidebar:
    st.title("🎯 Infeksius Actio")
    st.subheader("Filter Strategi")
    selected_strategy = st.multiselect(
        "Pilih Indikator:",
        ["MA 20 Cross", "MA 50 Cross", "RSI Oversold", "RSI Overbought", "MACD Golden Cross"],
        default=["MA 20 Cross", "RSI Oversold"]
    )
    min_volume = st.number_input("Min Volume (Juta)", value=1, help="Filter likuiditas saham")
    st.info("Scanner ini memantau saham IHSG secara real-time.")

# --- HEADER ---
st.title("📈 Swing Trading Scanner")
tab1, tab2, tab3 = st.tabs(["🔍 Scanner", "🔥 Market Heatmap", "📊 Stock Analysis"])

# --- DATA DUMMY / LIST SAHAM ---
# Di aplikasi asli, mereka menggunakan daftar saham IHSG (JK)
tickers = ["BBCA.JK", "BBRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "ADRO.JK", "UNTR.JK"]

@st.cache_data
def get_stock_data(symbols):
    results = []
    for s in symbols:
        try:
            df = yf.download(s, period="3mo", interval="1d", progress=False)
            if df.empty: continue
            
            # Hitung Indikator
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['MA20'] = ta.sma(df['Close'], length=20)
            
            last_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            change = ((last_price - prev_price) / prev_price) * 100
            
            # Logika Sinyal Sederhana
            signal = "Neutral"
            if last_price > df['MA20'].iloc[-1] and df['RSI'].iloc[-1] < 40:
                signal = "STRONG BUY"
            elif df['RSI'].iloc[-1] < 30:
                signal = "BUY (Oversold)"
            
            results.append({
                "Ticker": s,
                "Price": round(last_price, 2),
                "Change %": round(change, 2),
                "RSI": round(df['RSI'].iloc[-1], 2),
                "Signal": signal
            })
        except:
            continue
    return pd.DataFrame(results)

# --- ISI TAB 1: SCANNER ---
with tab1:
    st.subheader("Live Market Signals")
    data_scanner = get_stock_data(tickers)
    
    # Memberi warna pada kolom Signal
    def color_signal(val):
        color = 'red' if 'SELL' in str(val) else 'green' if 'BUY' in str(val) else 'black'
        return f'color: {color}; font-weight: bold'

    if not data_scanner.empty:
        st.dataframe(data_scanner.style.applymap(color_signal, subset=['Signal']), use_container_width=True)
    else:
        st.write("Sedang mengambil data...")

# --- ISI TAB 2: HEATMAP ---
with tab2:
    st.subheader("Market Heatmap (Top Performers)")
    if not data_scanner.empty:
        fig = px.treemap(data_scanner, path=['Ticker'], values='Price',
                         color='Change %', color_continuous_scale='RdYlGn',
                         hover_data=['RSI'])
        st.plotly_chart(fig, use_container_width=True)

# --- ISI TAB 3: ANALYSIS ---
with tab3:
    col1, col2 = st.columns()
    with col1:
        stock_to_analyze = st.selectbox("Pilih Saham:", tickers)
    
    with col2:
        st.write(f"Menampilkan analisis mendalam untuk **{stock_to_analyze}**")
        hist = yf.download(stock_to_analyze, period="6mo")
        st.line_chart(hist['Close'])

# --- FOOTER ---
st.markdown("---")
st.caption("Aplikasi ini dibuat untuk tujuan edukasi. Pastikan analisis kembali sebelum melakukan trading.")
