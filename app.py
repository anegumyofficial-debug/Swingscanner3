import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Infectious Actio Clone", layout="wide", page_icon="📈")

# --- 2. DATABASE SAHAM (Database Lengkap) ---
TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", 
    "BBNI.JK", "ADRO.JK", "UNVR.JK", "ANTM.JK", "CPIN.JK", "ICBP.JK",
    "MDKA.JK", "PGAS.JK", "PTBA.JK", "ITMG.JK", "AKRA.JK", "BRIS.JK"
]

# --- 3. LOGIKA PENGAMBILAN DATA (Anti-Limit) ---
@st.cache_data(ttl=3600)
def load_market_data(tickers):
    try:
        # Download massal agar efisien dan tidak kena blokir
        data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', progress=False)
        return data
    except Exception:
        return None

# --- 4. SIDEBAR (FILTER STRATEGI - Sama Persis Target) ---
with st.sidebar:
    st.title("📊 INFECTIOUS ACTIO")
    st.markdown("---")
    st.header("🔍 Filter & Strategi")
    
    # Filter yang ada di website referensi
    pilih_strategi = st.selectbox(
        "Pilih Strategi:", 
        ["Scalping (RSI < 30)", "Swing Trading (BB Bottom)", "Investment (Undervalued)"]
    )
    
    st.markdown("---")
    st.subheader("⚙️ Parameter")
    min_rsi = st.slider("Min RSI", 0, 100, 30)
    max_rsi = st.slider("Max RSI", 0, 100, 70)
    
    st.info("Scanner ini otomatis memfilter saham IDX yang masuk dalam area akumulasi.")

# --- 5. MAIN CONTENT ---
st.title("📈 Stock Screener Real-time")
st.write(f"Update Terakhir: **{datetime.now().strftime('%d %M %Y %H:%M')}**")

# Tampilan Tab seperti target
tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

# Ambil Data
raw_data = load_market_data(TICKERS)

def run_screener(label):
    if raw_data is None or raw_data.empty:
        st.error("Gagal menarik data dari IDX. Tunggu sebentar dan refresh (F5).")
        return

    results = []
    for t in TICKERS:
        try:
            df = raw_data[t].dropna()
            if len(df) < 30: continue
            
            # Indikator Teknikal
            df['RSI'] = ta.rsi(df['Close'], length=14)
            bb = ta.bbands(df['Close'], length=20, std=2)
            df['MA20'] = ta.sma(df['Close'], length=20)
            
            last = df.iloc[-1]
            last_bb = bb.iloc[-1]
            
            price = float(last['Close'])
            rsi_v = float(last['RSI'])
            
            # Ambil BB Lower & Upper secara aman
            bbl = float(last_bb.iloc) # Kolom BBL
            bbu = float(last_bb.iloc) # Kolom BBU
            
            # Logika Signal Persis Target
            signal = "HOLD"
            action_color = "white"
            
            if price <= bbl or rsi_v <= min_rsi:
                signal = "BUY"
                action_color = "#00ff00" # Hijau
            elif price >= bbu or rsi_v >= max_rsi:
                signal = "SELL"
                action_color = "#ff4b4b" # Merah
                
            results.append({
                "STOCK": t.replace(".JK", ""),
                "PRICE": int(price),
                "SIGNAL": signal,
                "RSI": round(rsi_v, 2),
                "L-BAND": int(bbl),
                "U-BAND": int(bbu),
                "_color": action_color
            })
        except:
            continue

    if results:
        df_final = pd.DataFrame(results)
        
        # Styling Tabel agar tampilan sinyal berwarna
        def style_rows(row):
            return [f'color: {row["_color"]}; font-weight: bold' if name == 'SIGNAL' else '' for name in row.index]

        st.dataframe(
            df_final.drop(columns=['_color']).style.apply(style_rows, axis=1),
            width="stretch", 
            hide_index=True
        )
    else:
        st.warning("Tidak ada saham yang masuk dalam kriteria saat ini.")

# Eksekusi Tab
with tab1: run_screener("Daily")
with tab2: run_screener("Weekly")
with tab3: run_screener("Monthly")

# --- 6. FOOTER / KALKULATOR (Opsi Tambahan) ---
st.markdown("---")
with st.expander("🧮 Kalkulator Average Down"):
    col1, col2 = st.columns(2)
    with col1:
        p1 = st.number_input("Harga Beli 1", value=1000)
        q1 = st.number_input("Lot 1", value=10)
    with col2:
        p2 = st.number_input("Harga Beli 2", value=800)
        q2 = st.number_input("Lot 2", value=10)
    
    if (q1 + q2) > 0:
        avg = ((p1 * q1) + (p2 * q2)) / (q1 + q2)
        st.success(f"Harga Rata-rata: {avg:,.0f}")
