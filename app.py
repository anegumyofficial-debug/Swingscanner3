import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Infectious Actio Clone", layout="wide", page_icon="📈")

# --- 2. DATABASE TICKER IHSG ---
TICKERS = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BBNI.JK", "ADRO.JK", "UNVR.JK", "ANTM.JK", "MEDC.JK"]

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=3600)
def load_market_data(tickers):
    try:
        # Download massal (lebih aman dari blokir)
        data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
        return data
    except Exception:
        return None

# --- 4. HEADER ---
st.title("📈 Infectious Actio Scanner V.3")
st.caption(f"Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

# Memuat data sekali saja untuk semua tab
raw_data = load_market_data(TICKERS)

def process_logic(label):
    if raw_data is None or raw_data.empty:
        st.error("Gagal memuat data. Server sedang sibuk (Rate Limit).")
        return

    rows = []
    for t in TICKERS:
        try:
            # Ambil data spesifik ticker
            df_t = raw_data[t].dropna()
            if len(df_t) < 30: continue
            
            # Indikator (RSI & BB)
            df_t['RSI'] = ta.rsi(df_t['Close'], length=14)
            bb = ta.bbands(df_t['Close'], length=20, std=2)
            
            # Ambil baris terakhir
            last = df_t.iloc[-1]
            last_bb = bb.iloc[-1]
            
            # Definisi Variabel secara Eksplisit (Mencegah NameError)
            price_val = float(last['Close'])
            rsi_val = float(last['RSI'])
            
            # Cari kolom BBL dan BBU secara dinamis
            bbl_col = [c for c in bb.columns if c.startswith('BBL')]
            bbu_col = [c for c in bb.columns if c.startswith('BBU')]
            
            l_band = float(last_bb[bbl_col])
            u_band = float(last_bb[bbu_col])
            
            # Logika Sinyal
            signal = "HOLD"
            zone = "NEUTRAL"
            
            if price_val <= l_band or rsi_val < 35:
                signal = "BUY"
                zone = "OVERSOLD"
            elif price_val >= u_band or rsi_val > 70:
                signal = "SELL"
                zone = "OVERBOUGHT"
                
            rows.append({
                "STOCK": t.replace(".JK", ""),
                "PRICE": int(price_val),
                "SIGNAL": signal,
                "ZONE": zone,
                "RSI": round(rsi_val, 2)
            })
        except Exception:
            continue

    if rows:
        df_display = pd.DataFrame(rows)
        
        # Pewarnaan Sinyal
        def style_signal(val):
            if val == 'BUY': return 'color: #00ff00; font-weight: bold'
            if val == 'SELL': return 'color: #ff4b4b; font-weight: bold'
            return ''
        
        # Gunakan width="stretch" (Fixing deprecation warning) 
        st.dataframe(
            df_display.style.map(style_signal, subset=['SIGNAL']), 
            width="stretch", 
            hide_index=True
        )
    else:
        st.warning("Data belum tersedia untuk timeframe ini.")

# --- 5. EKSEKUSI TAB ---
with tab1: process_logic("Daily")
with tab2: process_logic("Weekly")
with tab3: process_logic("Monthly")
