import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Infectious Actio Clone", layout="wide", page_icon="📈")

# --- DATABASE SAHAM (IHSG) ---
TICKERS = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BBNI.JK", "ADRO.JK", "UNVR.JK", "ANTM.JK", "MEDC.JK"]

# --- DATA ENGINE (Anti-Limit & Anti-Crash) ---
@st.cache_data(ttl=3600) # Data disimpan 1 jam untuk menghindari blokir API
def load_market_data(tickers):
    try:
        # Download massal (lebih aman dari blokir)
        data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
        return data
    except Exception:
        return None

# --- HEADER ---
st.title("📈 Infectious Actio Scanner V.3")
st.caption(f"Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

raw_data = load_market_data(TICKERS)

def process_logic(label):
    if raw_data is None or raw_data.empty:
        st.error("Gagal memuat data. Server Yahoo sedang membatasi akses (Rate Limit).")
        return

    rows = []
    for t in TICKERS:
        try:
            df = raw_data[t].dropna()
            if len(df) < 25: continue
            
            # Indikator (BB & RSI)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            bb = ta.bbands(df['Close'], length=20, std=2)
            
            latest = df.iloc[-1]
            # Perbaikan TypeError: Mengambil nilai angka murni
            price = float(latest['Close'])
            rsi_v = float(latest['RSI'])
            l_band = float(bb.iloc[-1, 0]) # Lower Band
            u_band = float(bb.iloc[-1, 2]) # Upper Band
            
            # Logic Sinyal Infectious Actio
            signal = "HOLD"
            zone = "NEUTRAL"
            if price <= l_band or rsi_v < 35:
                signal = "BUY"
                zone = "OVERSOLD"
            elif price >= u_band or rsi_v > 70:
                signal = "SELL"
                zone = "OVERBOUGHT"
                
            rows.append({
                "STOCK": t.replace(".JK", ""),
                "PRICE": f"{price:,.0f}",
                "SIGNAL": signal,
                "ZONE": zone,
                "RSI": round(rsi_v, 2)
            })
        except:
            continue

    if rows:
        df_display = pd.DataFrame(rows)
        # Warna Sinyal
        def color_val(v):
            if v == 'BUY': return 'color: #00ff00; font-weight: bold'
            if v == 'SELL': return 'color: #ff4b4b; font-weight: bold'
            return ''
        
        st.dataframe(df_display.style.applymap(color_val, subset=['SIGNAL']), use_container_width=True, hide_index=True)

with tab1: process_logic("Daily")
with tab2: process_logic("Weekly")
with tab3: process_logic("Monthly")
