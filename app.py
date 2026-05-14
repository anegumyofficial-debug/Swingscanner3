import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import concurrent.futures

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Infectious Actio Clone", layout="wide", page_icon="📈")

# --- 2. CUSTOM CSS (Visual Identik) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stDataFrame { border-radius: 10px; }
    div[data-testid="stExpander"] { border: none; box-shadow: none; }
    .buy-sig { color: #00ff00; font-weight: bold; background-color: rgba(0, 255, 0, 0.1); padding: 2px 5px; border-radius: 4px; }
    .sell-sig { color: #ff4b4b; font-weight: bold; background-color: rgba(255, 75, 75, 0.1); padding: 2px 5px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE TICKER IHSG ---
# Daftar saham ini bisa Anda tambah sesuai kebutuhan
TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", 
    "AMRT.JK", "BBNI.JK", "ADRO.JK", "UNVR.JK", "CPIN.JK", "ICBP.JK",
    "MDKA.JK", "PGAS.JK", "PTBA.JK", "ITMG.JK", "AKRA.JK", "BRIS.JK"
]

# --- 4. ENGINE ANALISIS (Logic & Fix TypeError) ---
@st.cache_data(ttl=3600) # Cache data selama 1 jam untuk menghindari limit API
def fetch_and_analyze(ticker, label):
    try:
        # Download data 6 bulan agar indikator stabil
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        
        # Kalkulasi Indikator Persis Target
        df['RSI'] = ta.rsi(df['Close'], length=14)
        bb = ta.bbands(df['Close'], length=20, std=2)
        df = pd.concat([df, bb], axis=1)
        
        # Ambil baris terakhir secara aman (Fixing Indexing Error)
        latest = df.iloc[-1]
        price = float(latest['Close'])
        rsi_val = float(latest['RSI'])
        
        # Identifikasi kolom Bollinger Bands secara dinamis
        l_band = float(latest.filter(like='BBL').iloc) 
        u_band = float(latest.filter(like='BBU').iloc)
        
        # Logika Sinyal
        signal = "HOLD"
        if price <= l_band or rsi_val < 35:
            signal = "BUY"
        elif price >= u_band or rsi_v > 70:
            signal = "SELL"
            
        return {
            "STOCK": ticker.replace(".JK", ""),
            "PRICE": f"{price:,.0f}",
            "SIGNAL": signal,
            "RSI": round(rsi_val, 2),
            "L-BAND": f"{l_band:,.0f}",
            "U-BAND": f"{u_band:,.0f}",
            "TIMEFRAME": label
        }
    except:
        return None

# --- 5. TAMPILAN UTAMA (HEADER & TABS) ---
st.title("📈 Infectious Actio - Swing Scanner")
st.caption(f"Status: Online • Terakhir Diperbarui: {datetime.now().strftime('%H:%M:%S')}")

tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

def render_scanner(tab, label):
    with tab:
        with st.spinner(f"Memindai database untuk {label}..."):
            results = []
            # Menggunakan Multithreading agar proses scan sangat cepat
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(fetch_and_analyze, t, label) for t in TICKERS]
                for f in concurrent.futures.as_completed(futures):
                    res = f.result()
                    if res: results.append(res)
            
            if results:
                df_final = pd.DataFrame(results)
                
                # Fungsi pewarnaan kolom SIGNAL
                def style_signal(val):
                    if val == 'BUY': return 'color: #00ff00; font-weight: bold'
                    if val == 'SELL': return 'color: #ff4b4b; font-weight: bold'
                    return ''

                st.dataframe(
                    df_final.style.applymap(style_signal, subset=['SIGNAL']),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.error("Gagal memuat data. API sedang dibatasi (Rate Limit). Silakan coba lagi nanti.")

# Eksekusi Tab
render_scanner(tab1, "Daily")
render_scanner(tab2, "Weekly")
render_scanner(tab3, "Monthly")

# --- 6. SIDEBAR MENU ---
with st.sidebar:
    st.header("📊 INFECTIOUS ACTIO")
    menu = st.selectbox("Menu Utama", ["Screener Saham", "Kalkulator Avg Down", "Harga Wajar"])
    
    if menu == "Kalkulator Avg Down":
        st.subheader("🧮 Kalkulator")
        p1 = st.number_input("Harga Beli 1", value=1000)
        q1 = st.number_input("Lot 1", value=10)
        p2 = st.number_input("Harga Beli 2", value=800)
        q2 = st.number_input("Lot 2", value=10)
        
        avg = ((p1 * q1) + (p2 * q2)) / (q1 + q2)
        st.metric("Harga Rata-rata", f"{avg:,.0f}")
