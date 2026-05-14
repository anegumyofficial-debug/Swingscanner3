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
@st.cache_data(ttl=3600)
def load_market_data(tickers):
    try:
        # Download massal (lebih aman dari blokir) [cite: 1, 2]
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
        st.error("Gagal memuat data. Server Yahoo sedang membatasi akses (Rate Limit).") [cite: 7]
        return

    rows = []
    for t in TICKERS:
        try:
            # Mengambil data per ticker [cite: 18]
            df = raw_data[t].dropna()
            if len(df) < 25: continue
            
            # Indikator (BB & RSI) [cite: 37, 52]
            df['RSI'] = ta.rsi(df['Close'], length=14)
            bb = ta.bbands(df['Close'], length=20, std=2)
            
            latest = df.iloc[-1] [cite: 56, 64]
            # Perbaikan TypeError: Mengambil nilai angka murni [cite: 26, 40]
            price = float(latest['Close']) [cite: 57]
            rsi_v = float(latest['RSI']) [cite: 58, 65]
            
            # Mendeteksi nama kolom Bollinger Bands secara otomatis [cite: 52, 55, 63, 66]
            l_col = [c for c in bb.columns if c.startswith('BBL')]
            u_col = [c for c in bb.columns if c.startswith('BBU')]
            
            l_band = float(bb[l_col].iloc[-1])
            u_band = float(bb[u_col].iloc[-1])
            
            # Logic Sinyal [cite: 62, 67]
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
                "PRICE": int(price),
                "SIGNAL": signal,
                "ZONE": zone,
                "RSI": round(rsi_v, 2)
            })
        except:
            continue

    if rows:
        df_display = pd.DataFrame(rows)
        
        # PERBAIKAN ATTRIBUTEERROR: Ganti applymap menjadi map (untuk Streamlit terbaru)
        def color_val(v):
            if v == 'BUY': return 'color: #00ff00; font-weight: bold'
            if v == 'SELL': return 'color: #ff4b4b; font-weight: bold'
            return ''
        
        # PERBAIKAN: Gunakan width="stretch" sebagai pengganti use_container_width [cite: 88, 90, 94]
        st.dataframe(
            df_display.style.map(color_val, subset=['SIGNAL']), 
            width="stretch", 
            hide_index=True
        )
    else:
        st.warning("Data belum tersedia untuk timeframe ini.")

with tab1: process_logic("Daily") [cite: 105]
with tab2: process_logic("Weekly") [cite: 106]
with tab3: process_logic("Monthly") [cite: 107]
