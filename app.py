import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Infectious Actio Clone", layout="wide")

# 2. CSS Custom (Agar Mirip Target)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { font-size: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# 3. Database Ticker IHSG
TICKERS = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "AMRT.JK", "BBNI.JK"]

# 4. Fungsi Ambil Data dengan Cache (Mencegah Limit API)
@st.cache_data(ttl=3600)
def fetch_market_data(tickers):
    try:
        # Download massal lebih aman dari rate limit
        data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
        return data
    except Exception:
        return None

# 5. UI Utama
st.title("📈 Infectious Actio Clone")
st.caption(f"Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

raw_data = fetch_market_data(TICKERS)

def process_scanner(label):
    if raw_data is None or raw_data.empty:
        st.error("Gagal memuat data. Periksa limit API Yahoo Finance.")
        return

    results = []
    for t in TICKERS:
        try:
            df_t = raw_data[t].dropna()
            if len(df_t) < 20: continue
            
            # Indikator
            df_t['RSI'] = ta.rsi(df_t['Close'], length=14)
            bb = ta.bbands(df_t['Close'], length=20, std=2)
            
            last = df_t.iloc[-1]
            last_bb = bb.iloc[-1]
            
            price = float(last['Close'])
            rsi_v = float(last['RSI'])
            l_band = float(last_bb.iloc) # BBL
            u_band = float(last_bb.iloc[2]) # BBU
            
            # Logika Signal
            signal = "HOLD"
            if price <= l_band or rsi_v < 35: signal = "BUY"
            elif price >= u_band or rsi_v > 70: signal = "SELL"
            
            results.append({
                "STOCK": t.replace(".JK", ""),
                "PRICE": int(price),
                "SIGNAL": signal,
                "RSI": round(rsi_v, 2),
                "ZONE": "OVERSOLD" if rsi_v < 35 else "OVERBOUGHT" if rsi_v > 70 else "NEUTRAL"
            })
        except:
            continue

    if results:
        df_res = pd.DataFrame(results)
        def color_signal(val):
            color = '#00ff00' if val == 'BUY' else '#ff4b4b' if val == 'SELL' else 'white'
            return f'color: {color}; font-weight: bold'
        
        st.dataframe(df_res.style.applymap(color_signal, subset=['SIGNAL']), use_container_width=True, hide_index=True)

with tab1: process_scanner("Daily")
with tab2: process_scanner("Weekly")
with tab3: process_scanner("Monthly")
