import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Infectious Actio Clone", layout="wide", page_icon="📈")

# --- 2. DATABASE TICKER SAHAM IDX ---
# Menarik data saham populer di Bursa Efek Indonesia
TICKERS = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BBNI.JK", "ADRO.JK", "UNVR.JK", "ANTM.JK"]

# --- 3. DATA ENGINE (Mencegah Limit API) ---
@st.cache_data(ttl=3600)
def load_idx_data(tickers):
    try:
        # Download massal satu kali untuk semua saham agar tidak kena blokir
        data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
        return data
    except Exception:
        return None

# --- 4. HEADER ---
st.title("📈 Infectious Actio Scanner V.3")
st.caption(f"Sinkronisasi Terakhir: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

# Memanggil data dari Yahoo Finance
raw_data = load_idx_data(TICKERS)

def process_logic(label):
    if raw_data is None or raw_data.empty:
        st.error("Gagal memuat data. Server sedang sibuk atau limit API tercapai.")
        return

    rows = []
    for t in TICKERS:
        try:
            # Ambil data per saham dan hapus nilai kosong
            df_t = raw_data[t].dropna()
            if len(df_t) < 30: continue
            
            # Indikator Teknikal (RSI & Bollinger Bands)
            df_t['RSI'] = ta.rsi(df_t['Close'], length=14)
            bb = ta.bbands(df_t['Close'], length=20, std=2)
            
            last_bar = df_t.iloc[-1]
            last_bb = bb.iloc[-1]
            
            # Ambil nilai harga dan indikator secara aman
            price_val = float(last_bar['Close'])
            rsi_val = float(last_bar['RSI'])
            
            # Deteksi kolom Bollinger Bands secara dinamis
            bbl_col = [c for c in bb.columns if c.startswith('BBL')]
            u_col = [c for c in bb.columns if c.startswith('BBU')]
            
            l_band = float(last_bb[bbl_col])
            u_band = float(last_bb[u_col])
            
            # Logika Sinyal Persis Target
            signal = "HOLD"
            zone = "NEUTRAL"
            if price_val <= l_band or rsi_val < 35:
                signal = "BUY"
                zone = "OVERSOLD"
            elif price_val >= u_band or rsi_val > 70:
                signal = "SELL"
                zone = "OVERBOUGHT"
                
            rows.append({
                "SAHAM": t.replace(".JK", ""),
                "HARGA": int(price_val),
                "SINYAL": signal,
                "ZONE": zone,
                "RSI": round(rsi_val, 2)
            })
        except Exception:
            continue

    if rows:
        df_display = pd.DataFrame(rows)
        
        # Pewarnaan Sinyal: Hijau untuk BUY, Merah untuk SELL
        def color_signal(val):
            if val == 'BUY': return 'color: #00ff00; font-weight: bold'
            if val == 'SELL': return 'color: #ff4b4b; font-weight: bold'
            return ''
        
        st.dataframe(
            df_display.style.map(color_signal, subset=['SINYAL']), 
            width="stretch", 
            hide_index=True
        )
    else:
        st.warning("Data belum tersedia untuk saat ini.")

# --- 5. EKSEKUSI TAB ---
with tab1: process_logic("Daily")
with tab2: process_logic("Weekly")
with tab3: process_logic("Monthly")
