import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Infectious Actio - Official Clone", layout="wide", page_icon="📈")

# --- DATABASE SAHAM IHSG (Sesuai Target) ---
TICKERS = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "AMRT.JK", "BBNI.JK", "ADRO.JK", "UNVR.JK", "CPIN.JK", "ICBP.JK"]

# --- FUNGSI SCANNER ---
@st.cache_data(ttl=3600) # Simpan data selama 1 jam agar tidak kena limit
def get_market_data(tickers):
    try:
        # Download massal (Lebih cepat & aman dari limit)
        data = yf.download(tickers, period="3mo", interval="1d", group_by='ticker', progress=False)
        return data
    except:
        return None

def analyze_logic(df_ticker):
    # Kalkulasi Indikator
    df_ticker['RSI'] = ta.rsi(df_ticker['Close'], length=14)
    bb = ta.bbands(df_ticker['Close'], length=20, std=2)
    
    last_row = df_ticker.iloc[-1]
    price = last_row['Close']
    rsi_v = last_row['RSI']
    # Ambil Lower/Upper Band secara manual dari dataframe BB
    l_band = bb.iloc[-1, 0] # BBL_20_2.0
    u_band = bb.iloc[-1, 2] # BBU_20_2.0
    
    # Logic Sinyal Persis Target
    signal = "HOLD"
    color = "white"
    if price <= l_band or rsi_v < 35:
        signal = "BUY"
        color = "#00ff00"
    elif price >= u_band or rsi_v > 70:
        signal = "SELL"
        color = "#ff4b4b"
        
    return price, signal, rsi_v, l_band, u_band, color

# --- TAMPILAN UTAMA ---
st.title("📈 Infectious Actio Scanner")

tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

raw_data = get_market_data(TICKERS)

def render_tab(tab_name):
    if raw_data is None or raw_data.empty:
        st.error("Gagal memuat data dari Yahoo Finance. Coba refresh beberapa saat lagi.")
        return

    results = []
    for t in TICKERS:
        try:
            ticker_df = raw_data[t].dropna()
            price, sig, rsi, lb, ub, col = analyze_logic(ticker_df)
            results.append({
                "STOCK": t.replace(".JK", ""),
                "PRICE": f"{price:,.0f}",
                "SIGNAL": sig,
                "RSI": f"{rsi:.2f}",
                "L-BAND": f"{lb:,.0f}",
                "U-BAND": f"{ub:,.0f}",
                "_color": col
            })
        except:
            continue

    if results:
        df_display = pd.DataFrame(results)
        
        # Styling baris berdasarkan sinyal
        def style_rows(row):
            return [f'color: {row["_color"]}; font-weight: bold' if name == 'SIGNAL' else '' for name in row.index]

        st.dataframe(
            df_display.drop(columns=['_color']).style.apply(style_rows, axis=1),
            use_container_width=True,
            hide_index=True
        )

with tab1: render_tab("Day")
with tab2: render_tab("Week")
with tab3: render_tab("Month")

# --- FOOTER ---
st.divider()
st.caption("Data diperbarui otomatis setiap jam untuk menghindari pembatasan API.")
