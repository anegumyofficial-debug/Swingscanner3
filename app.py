import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

# Konfigurasi agar tidak crash
st.set_page_config(page_title="Infectious Actio Clone", layout="wide")

# Database saham
TICKERS = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BBNI.JK"]

# FUNGSI CACHE (Ini yang membuat data muncul & tidak kena blokir)
@st.cache_data(ttl=3600)
def get_data(tickers):
    try:
        return yf.download(tickers, period="3mo", interval="1d", group_by='ticker', progress=False)
    except:
        return None

st.title("📈 Infectious Actio Scanner")

data = get_data(TICKERS)

if data is not None and not data.empty:
    results = []
    for t in TICKERS:
        try:
            df = data[t].dropna()
            df['RSI'] = ta.rsi(df['Close'], length=14)
            bb = ta.bbands(df['Close'], length=20, std=2)
            
            # Perbaikan TypeError: Ambil nilai angka secara benar
            price = float(df['Close'].iloc[-1])
            rsi_v = float(df['RSI'].iloc[-1])
            l_band = float(bb.iloc[-1, 0]) # Lower Band
            
            results.append({
                "STOCK": t.replace(".JK", ""),
                "PRICE": f"{price:,.0f}",
                "SIGNAL": "BUY" if price <= l_band else "HOLD",
                "RSI": f"{rsi_v:.2f}"
            })
        except:
            continue
    
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
    else:
        st.warning("Data sedang diproses...")
else:
    st.error("Server sedang sibuk (Rate Limit). Tunggu 1 menit lalu refresh.")
