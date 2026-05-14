import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Infectious Actio Clone", layout="wide", page_icon="📈")

# --- 2. STYLE CSS (REPLIKA VISUAL) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #ffffff; 
        border-radius: 5px 5px 0px 0px; 
        padding: 10px 20px;
        font-weight: bold;
    }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE SAHAM IDX ---
TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", 
    "BBNI.JK", "ADRO.JK", "UNVR.JK", "ANTM.JK", "CPIN.JK", "ICBP.JK",
    "MDKA.JK", "PGAS.JK", "PTBA.JK", "ITMG.JK", "AKRA.JK", "BRIS.JK"
]

# --- 4. DATA ENGINE (MASS DOWNLOAD & CACHE) ---
@st.cache_data(ttl=3600)
def load_idx_data(tickers):
    try:
        # Mengambil data 1 tahun agar indikator stabil
        data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', progress=False)
        return data
    except Exception:
        return None

# --- 5. SIDEBAR (FILTER STRATEGI) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2422/2422796.png", width=50)
    st.title("INFECTIOUS ACTIO")
    st.markdown("---")
    st.header("🎯 Filter Strategi")
    
    strat_type = st.radio("Mode Screening:", ["Swing Trading", "Day Scalping", "Long Invest"])
    
    st.markdown("---")
    rsi_range = st.slider("Range RSI (Oversold/Overbought)", 0, 100, (30, 70))
    st.info("Scanner akan menyaring saham berdasarkan area akumulasi Bollinger Bands.")

# --- 6. MAIN DASHBOARD ---
st.title("📈 Market Scanner Real-time")
st.write(f"Sinkronisasi Terakhir: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")

tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

raw_data = load_idx_data(TICKERS)

def process_screener(label):
    if raw_data is None or raw_data.empty:
        st.error("Gagal menarik data dari server IDX. Mohon tunggu 1 menit dan refresh.")
        return

    final_rows = []
    for t in TICKERS:
        try:
            # Ambil data per ticker
            df_t = raw_data[t].dropna()
            if len(df_t) < 40: continue
            
            # Indikator Teknikal (Presisi)
            df_t['RSI'] = ta.rsi(df_t['Close'], length=14)
            df_t['EMA20'] = ta.ema(df_t['Close'], length=20)
            bb = ta.bbands(df_t['Close'], length=20, std=2)
            
            last = df_t.iloc[-1]
            last_bb = bb.iloc[-1]
            
            price = float(last['Close'])
            rsi_val = float(last['RSI'])
            ema_val = float(last['EMA20'])
            
            # Deteksi BBL/BBU secara dinamis (Anti-Crash)
            bbl_col = [c for c in bb.columns if c.startswith('BBL')]
            u_col = [c for c in bb.columns if c.startswith('BBU')]
            l_band = float(last_bb[bbl_col])
            u_band = float(last_bb[u_col])
            
            # Logic Sinyal Identik
            signal = "HOLD"
            zone = "NEUTRAL"
            trend = "🟢 Bullish" if price > ema_val else "🔴 Bearish"
            
            if price <= l_band or rsi_val <= rsi_range:
                signal = "BUY"
                zone = "ACCUMULATION"
            elif price >= u_band or rsi_val >= rsi_range[1]:
                signal = "SELL"
                zone = "DISTRIBUTION"
                
            final_rows.append({
                "STOCK": t.replace(".JK", ""),
                "PRICE": int(price),
                "SIGNAL": signal,
                "TREND": trend,
                "ZONE": zone,
                "RSI": round(rsi_val, 2),
                "MA-20": int(ema_val)
            })
        except:
            continue

    if final_rows:
        df_display = pd.DataFrame(final_rows)
        
        # Styling baris sinyal (Hijau untuk BUY, Merah untuk SELL)
        def style_rows(row):
            if row['SIGNAL'] == 'BUY':
                return ['color: #28a745; font-weight: bold'] * len(row)
            elif row['SIGNAL'] == 'SELL':
                return ['color: #dc3545; font-weight: bold'] * len(row)
            return [''] * len(row)

        st.dataframe(
            df_display.style.apply(style_rows, axis=1),
            width="stretch", 
            hide_index=True
        )
    else:
        st.warning("Tidak ada saham yang memenuhi kriteria filter saat ini.")

# Menjalankan fungsi di setiap tab
with tab1: process_screener("Daily")
with tab2: process_screener("Weekly")
with tab3: process_screener("Monthly")
