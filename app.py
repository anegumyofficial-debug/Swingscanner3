import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import concurrent.futures

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Infectious Actio Clone", layout="wide", page_icon="📈")

# --- 2. STYLE CSS (Identik dengan Target) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stDataFrame { border-radius: 10px; border: 1px solid #e6e9ef; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE TICKER IHSG (Lengkap) ---
TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", 
    "AMRT.JK", "BBNI.JK", "ADRO.JK", "UNVR.JK", "CPIN.JK", "ICBP.JK",
    "MDKA.JK", "PGAS.JK", "PTBA.JK", "ITMG.JK", "AKRA.JK", "BRIS.JK",
    "ANTM.JK", "ASSA.JK", "BBTN.JK", "BUKA.JK", "KLBF.JK", "MEDC.JK"
]

# --- 4. CORE LOGIC SCANNER (Presisi) ---
@st.cache_data(ttl=3600)
def fetch_and_analyze(ticker):
    try:
        # Ambil data lebih panjang agar indikator (MA/BB) stabil
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty or len(df) < 50: return None
        
        # Indikator Teknikal Persis Target
        df['RSI'] = ta.rsi(df['Close'], length=14)
        bb = ta.bbands(df['Close'], length=20, std=2)
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df = pd.concat([df, bb], axis=1)
        
        # Penanganan Data Terakhir
        latest = df.iloc[-1]
        price = float(latest['Close'])
        rsi_val = float(latest['RSI'])
        ema_val = float(latest['EMA20'])
        
        # Ambil Bollinger Bands secara aman (Fixing TypeError)
        l_band = float(latest.filter(like='BBL').iloc)
        u_band = float(latest.filter(like='BBU').iloc)
        
        # Logika Sinyal Infectious Actio
        # Buy: Harga di bawah BB Low ATAU RSI di bawah 30 (Oversold)
        # Sell: Harga di atas BB High ATAU RSI di atas 70 (Overbought)
        status = "HOLD"
        zone = "NEUTRAL"
        
        if price <= l_band or rsi_val < 35:
            status = "BUY"
            zone = "ACCUMULATION"
        elif price >= u_band or rsi_val > 70:
            status = "SELL"
            zone = "DISTRIBUTION"
            
        return {
            "Kode": ticker.replace(".JK", ""),
            "Price": int(price),
            "Signal": status,
            "Trend": "Bullish" if price > ema_val else "Bearish",
            "Zone": zone,
            "RSI": round(rsi_val, 2),
            "MA20": int(ema_val)
        }
    except:
        return None

# --- 5. UI HEADER & TABS ---
st.title("📈 Infectious Actio Scanner V.3")
st.caption(f"Last Update: {datetime.now().strftime('%d %B %Y %H:%M')}")

tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

def render_table(label):
    with st.spinner(f"Memproses Database {label}..."):
        results = []
        # Multi-threading agar scan sangat cepat (fix error lambat)
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(fetch_and_analyze, t) for t in TICKERS]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res: results.append(res)
        
        if results:
            df_final = pd.DataFrame(results)
            
            # Styling agar warna teks Buy/Sell muncul persis target
            def style_signal(val):
                if val == 'BUY': return 'color: #28a745; font-weight: bold; background-color: #e6f4ea'
                if val == 'SELL': return 'color: #dc3545; font-weight: bold; background-color: #fce8e8'
                return ''

            st.dataframe(
                df_final.style.applymap(style_signal, subset=['Signal']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Gagal memuat data. API sedang dibatasi (Rate Limit). Silakan coba lagi nanti.")

with tab1: render_table("Scalping")
with tab2: render_table("Swing")
with tab3: render_table("Invest")

# --- 6. SIDEBAR MENU ---
with st.sidebar:
    st.header("📊 MENU UTAMA")
    menu = st.radio("Navigasi", ["Scanner Saham", "Average Down Calc", "Cek Harga Wajar"])
    
    if menu == "Average Down Calc":
        st.subheader("🧮 Kalkulator")
        buy_p = st.number_input("Harga Beli Sekarang", value=1000)
        lot_p = st.number_input("Jumlah Lot", value=10)
        new_p = st.number_input("Harga Beli Baru", value=800)
        new_lot = st.number_input("Lot Tambahan", value=10)
        
        total_m = (buy_p * lot_p) + (new_p * new_lot)
        avg = total_m / (lot_p + new_lot)
        st.success(f"Harga Rata-rata Baru: {avg:,.0f}")
