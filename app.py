import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import concurrent.futures

# --- CONFIG ---
st.set_page_config(page_title="Swing Trading Scanner", layout="wide")

# --- DATA SAHAM (Sesuai database IHSG) ---
# Tambahkan kode saham lainnya sesuai keinginan
TICKERS = ["BBRI.JK", "BBCA.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "AMRT.JK", "BBNI.JK", "ADRO.JK", "UNVR.JK"]

# --- ANALYTICS ENGINE ---
def fetch_and_analyze(ticker, label):
    try:
        # Mengambil data 1 tahun agar MA200 & indikator stabil
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty or len(df) < 50: return None
        
        # Kalkulasi Indikator Persis Target
        df['RSI'] = ta.rsi(df['Close'], length=14)
        bb = ta.bbands(df['Close'], length=20, std=2)
        # Menggabungkan BB ke dataframe utama
        df = pd.concat([df, bb], axis=1)
        
        # Ambil baris terakhir secara aman [cite: 59, 65]
        latest = df.iloc[-1]
        price = float(latest['Close'])
        rsi_val = float(latest['RSI'])
        
        # Identifikasi kolom Bollinger Bands secara dinamis
        bbl = float(latest.filter(like='BBL').iloc) # Lower Band [cite: 55]
        bbu = float(latest.filter(like='BBU').iloc) # Upper Band
        
        # Logika Signal
        signal = "HOLD"
        color = "white"
        if price <= bbl or rsi_val < 35:
            signal = "BUY"
            color = "#00ff00" # Hijau
        elif price >= bbu or rsi_val > 70:
            signal = "SELL"
            color = "#ff4b4b" # Merah

        return {
            "Kode": ticker.replace(".JK", ""),
            "Price": int(price),
            "Signal": signal,
            "RSI": round(rsi_val, 2),
            "L-Band": int(bbl),
            "U-Band": int(bbu),
            "Timeframe": label
        }
    except Exception:
        return None

# --- UI LAYOUT ---
st.title("📈 Infectious Actio Clone")
st.caption(f"Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Sidebar
with st.sidebar:
    st.header("🔍 Control Panel")
    st.subheader("Menu Utama")
    opt = st.radio("Pilih Alat:", ["Screener Saham", "Kalkulator Average Down", "Harga Wajar"])
    
    st.divider()
    st.write("Status: **Active**")

# Main Content
if opt == "Screener Saham":
    tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])
    
    def render_view(tab, label):
        with tab:
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_ticker = {executor.submit(fetch_and_analyze, t, label): t for t in TICKERS}
                for future in concurrent.futures.as_completed(future_to_ticker):
                    data = future.result()
                    if data: results.append(data)
            
            if results:
                df_res = pd.DataFrame(results)
                
                # Styling Tabel agar Mirip
                def style_signal(val):
                    if val == 'BUY': return 'background-color: rgba(0, 255, 0, 0.2); color: #00ff00; font-weight: bold'
                    if val == 'SELL': return 'background-color: rgba(255, 0, 0, 0.2); color: #ff4b4b; font-weight: bold'
                    return ''

                st.dataframe(
                    df_res.style.applymap(style_signal, subset=['Signal']),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.error("Gagal memuat data. Periksa koneksi atau limit API.")

    render_view(tab1, "Daily")
    render_view(tab2, "Weekly")
    render_view(tab3, "Monthly")

elif opt == "Kalkulator Average Down":
    st.subheader("🧮 Kalkulator Average Down")
    col1, col2 = st.columns(2)
    with col1:
        p1 = st.number_input("Harga Beli Awal", value=1000)
        l1 = st.number_input("Lot Awal", value=10)
    with col2:
        p2 = st.number_input("Harga Beli Baru", value=800)
        l2 = st.number_input("Lot Baru", value=10)
    
    total_modal = (p1 * l1 * 100) + (p2 * l2 * 100)
    total_lot = l1 + l2
    avg_price = total_modal / (total_lot * 100)
    
    st.metric("Harga Rata-rata Baru", f"{avg_price:,.2f}")
