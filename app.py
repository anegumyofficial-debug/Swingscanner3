import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(layout="wide", page_title="Master Stock Scanner Pro")

# 2. CSS CUSTOM UNTUK TAMPILAN PERSIS REFERENSI
st.markdown("""
    <style>
    /* Mengatur jarak antar kolom metric agar lebih rapat */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px !important;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Menghilangkan margin berlebih pada judul */
    .st-emotion-cache-10trblm { margin-top: -50px; }
    /* Mempercantik tabel */
    .stDataFrame { border: 1px solid #e0e0e0; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Master Stock Scanner - Pro Dashboard")
st.write(f"Update Terakhir: {datetime.now().strftime('%d %B %Y %H:%M')} WIB")
st.markdown("---")

# 3. LOGIKA PENGAMBILAN DATA (Selalu ambil nilai terupdate)
def get_analysis(ticker, label):
    config = {
        "Day (Scalping)": {"period": "1mo", "interval": "1h", "rsi_low": 30},
        "Weekly (Swing)": {"period": "6mo", "interval": "1d", "rsi_low": 40},
        "Monthly (Invest)": {"period": "2y", "interval": "1wk", "rsi_low": 45}
    }
    c = config[label]
    df = yf.download(ticker, period=c['period'], interval=c['interval'], progress=False, auto_adjust=True)
    
    if df is None or df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

    # Indikator
    df['RSI'] = ta.rsi(df['Close'], length=14)
    bb = ta.bbands(df['Close'], length=20, std=2)
    df = pd.concat([df, bb], axis=1).dropna(subset=['Close', 'RSI'])
    
    # Ambil baris terakhir yang valid (Meskipun pasar tutup tetap muncul)
    last = df.iloc[-1]
    price = round(float(last['Close']), 0)
    rsi_val = round(float(last['RSI']), 2)
    l_band = round(float(last.filter(like='BBL').iloc), 0)
    u_band = round(float(last.filter(like='BBU').iloc), 0)

    # Logika Status Warna
    if rsi_val <= c['rsi_low'] or price <= l_band:
        status, signal = "🟢 SIAP SEROK", "buy"
    elif rsi_val >= (100 - c['rsi_low']) or price >= u_band:
        status, signal = "🔴 JUAL / PROFIT", "sell"
    else:
        status, signal = "⚪ WAIT / NEUTRAL", "neutral"

    return {"Saham": ticker.replace(".JK", ""), "Harga": price, "Status": status, "RSI": rsi_val, "sig": signal}

# 4. IMPLEMENTASI BAR METRIC & TABEL DETAIL
tickers = ["BBRI.JK", "BBCA.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "BMRI.JK"]
tab1, tab2, tab3 = st.tabs(["🕒 Day Scalping", "📅 Weekly Swing", "🏛️ Monthly Invest"])

def render_tab(tab, label):
    with tab:
        res_list = []
        for t in tickers:
            data = get_analysis(t, label)
            if data: res_list.append(data)
        
        if res_list:
            df_final = pd.DataFrame(res_list)
            
            # --- BAR METRIC (SAMA PERSIS REFERENSI) ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Pantauan", f"{len(tickers)} Saham")
            m2.metric("Siap Serok", len(df_final[df_final['sig'] == 'buy']))
            m3.metric("Waktunya Jual", len(df_final[df_final['sig'] == 'sell']))
            m4.metric("Posisi Wait", len(df_final[df_final['sig'] == 'neutral']))
            
            st.markdown("### 📋 Detail Analisis")
            
            # Fungsi Warna Baris
            def apply_color(v):
                if "SEROK" in str(v): return 'background-color: #d4edda; color: #155724; font-weight: bold'
                if "JUAL" in str(v): return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                return ''

            st.dataframe(
                df_final.drop(columns=['sig']).style.applymap(apply_color, subset=['Status']),
                use_container_width=True
            )

render_tab(tab1, "Day (Scalping)")
render_tab(tab2, "Weekly (Swing)")
render_tab(tab3, "Monthly (Invest)")
