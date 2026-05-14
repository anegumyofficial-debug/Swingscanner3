import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

# --- KONTROL LAYOUT ---
st.set_page_config(page_title="Infectious Actio - Scanner", layout="wide")

# --- DATABASE SAHAM (Sesuai Target) ---
# Tambahkan ticker di sini untuk memperbanyak list saham
TICKERS = ["BBRI.JK", "BBCA.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "AMRT.JK", "BBNI.JK", "ADRO.JK", "UNVR.JK", "CPIN.JK", "ICBP.JK"]

# --- FUNGSI AMBIL DATA (Mencegah Limit API) ---
@st.cache_data(ttl=3600)
def load_data(tickers):
    try:
        # Download massal (Satu request untuk semua saham agar tidak kena limit)
        data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', progress=False)
        return data
    except Exception as e:
        return None

# --- HEADER ---
st.title("📈 Infectious Actio Clone")
st.caption(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- TAMPILAN TAB ---
tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

# Eksekusi Pengambilan Data
raw_data = load_data(TICKERS)

def show_scanner_table():
    if raw_data is None or raw_data.empty:
        st.error("Gagal menarik data dari server. Silakan refresh halaman (F5) dalam beberapa saat.")
        return

    all_results = []
    for t in TICKERS:
        try:
            # Ambil data per ticker dan hapus nilai kosong (NaN)
            df_stock = raw_data[t].dropna()
            if len(df_stock) < 30: continue
            
            # Kalkulasi Indikator
            df_stock['RSI'] = ta.rsi(df_stock['Close'], length=14)
            bb = ta.bbands(df_stock['Close'], length=20, std=2)
            
            last = df_stock.iloc[-1]
            last_bb = bb.iloc[-1]
            
            price = float(last['Close'])
            rsi_v = float(last['RSI'])
            l_band = float(last_bb.iloc) # BBL_20_2.0
            u_band = float(last_bb.iloc[2]) # BBU_20_2.0
            
            # Logika Signal Persis Target
            signal = "HOLD"
            zone = "NEUTRAL"
            if price <= l_band or rsi_v < 35:
                signal = "BUY"
                zone = "OVERSOLD"
            elif price >= u_band or rsi_v > 70:
                signal = "SELL"
                zone = "OVERBOUGHT"
            
            all_results.append({
                "STOCK": t.replace(".JK", ""),
                "PRICE": f"{price:,.0f}",
                "SIGNAL": signal,
                "RSI": f"{rsi_v:.2f}",
                "L-BAND": f"{lb:,.0f}" if 'lb' in locals() else f"{l_band:,.0f}",
                "U-BAND": f"{ub:,.0f}" if 'ub' in locals() else f"{u_band:,.0f}",
                "ZONE": zone
            })
        except:
            continue

    if all_results:
        df_final = pd.DataFrame(all_results)
        
        # Pewarnaan kolom SIGNAL agar sama dengan target
        def color_signal(val):
            if val == 'BUY': return 'background-color: rgba(0, 255, 0, 0.2); color: #00ff00; font-weight: bold'
            if val == 'SELL': return 'background-color: rgba(255, 0, 0, 0.2); color: #ff4b4b; font-weight: bold'
            return ''

        st.dataframe(
            df_final.style.applymap(color_signal, subset=['SIGNAL']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Data sedang diproses atau tidak tersedia.")

# Tampilkan di semua Tab
with tab1: show_scanner_table()
with tab2: show_scanner_table()
with tab3: show_scanner_table()
