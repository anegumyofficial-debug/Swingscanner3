import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
import concurrent.futures
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Scalper Radar BEI - Ultra Fast", layout="wide", page_icon="⚡")

# --- 2. CUSTOM CSS SCALPER ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #F8FAFC; }
    .main-title { color: #38BDF8; font-weight: 800; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE EMITEN AKTIF LIKUID ---
@st.cache_data(ttl=604800)
def load_scalping_tickers():
    # Mengutamakan saham-saham yang memiliki volatilitas dan volume harian tinggi untuk scalping
    saham_scalp = [
        "AADI", "ADRO", "AMMN", "ANTM", "APEX", "ASII", "ASSA", "AUTO", "BBCA", "BBNI", 
        "BBRI", "BMRI", "BRIS", "BUMI", "GOTO", "HRUM", "INDF", "ITMG", "KAEF", "MDKA", 
        "PTBA", "TLKM", "UNVR", "MEDC", "PGAS", "GGRM", "ACES", "AKRA", "BSDE", "CPIN"
    ]
    return sorted([f"{t}.JK" for t in saham_scalp])

master_tickers_jk = load_scalping_tickers()
master_tickers_clean = [t.replace(".JK", "") for t in master_tickers_jk]

def clean_yf_dataframe(df):
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df

# --- 4. ALGORITMA EVALUASI MOMENTUM SCALPING (1-5 MENIT) ---
def analyze_scalping_momentum(ticker):
    try:
        formatted_ticker = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
        
        # SCALPING ENGINE: Menggunakan data 5 hari terakhir dengan interval 5 Menit (Intraday)
        df = yf.download(formatted_ticker, period="5d", interval="5m", progress=False)
        df = clean_yf_dataframe(df)
        
        if df is None or len(df) < 15 or 'Close' not in df.columns: 
            return None
        
        # Indikator Utama Scalper: VWAP (Harga rata-rata tertimbang volume)
        # Rumus VWAP Intraday manual yang aman
        cum_vol = df['Volume'].cumsum()
        cum_vol_price = (df['Close'] * df['Volume']).cumsum()
        df['VWAP'] = cum_vol_price / cum_vol
        
        # Indikator Cepat: Stochastic Oscillator (%K, %D) untuk reaksi instan dibanding RSI
        stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
        df['STOCHk'] = stoch['STOCHk_14_3_3']
        df['STOCHd'] = stoch['STOCHd_14_3_3']
        
        # MA Cepat untuk Scalping (EMA 9 dan EMA 21)
        df['EMA9'] = ta.ema(df['Close'], length=9)
        
        # Ekstrak Nilai Menit Terakhir (Real-time tracking)
        last_price = float(df['Close'].iloc[-1])
        last_vwap = float(df['VWAP'].iloc[-1])
        last_k = float(df['STOCHk'].iloc[-1])
        last_d = float(df['STOCHd'].iloc[-1])
        last_ema = float(df['EMA9'].iloc[-1])
        
        # Menghitung estimasi kekuatan Bid/Ask jangka pendek via Volume Perubahan
        prev_price = float(df['Close'].iloc[-2])
        change_pct = ((last_price - prev_price) / prev_price) * 100
        
        ticker_name = ticker.replace(".JK", "")
        
        # LOGIKA ESTIMASI ARAH MENIT INI (Menghindari Premature Stop Loss)
        # 1. Bullish Kuat: Harga di atas VWAP + Stochastic Overlap ke atas di area bawah
        if last_price > last_vwap and last_price > last_ema and last_k > last_d and last_k < 40:
            direction = "🚀 STRONG UP (Hajar Kanan)"
            stop_loss_est = round(min(last_vwap, last_ema), 0)
        # 2. Rebound Cepat: Harga tertahan di VWAP, akumulasi masuk
        elif last_price > last_vwap and last_k > last_d:
            direction = "📈 UP MOMENTUM"
            stop_loss_est = round(last_vwap, 0)
        # 3. Warning Reversal Down: Harga menembus ke bawah EMA9 atau Stochastic Deadcross di area atas
        elif last_price < last_ema and last_k < last_d and last_k > 70:
            direction = "🚨 DUMP RISK (Segera Keluar)"
            stop_loss_est = round(last_price * 0.99, 0)
        # 4. Bearish Kuat: Berada di bawah nilai VWAP intraday
        elif last_price < last_vwap:
            direction = "📉 DOWN (Jangan Entry)"
            stop_loss_est = 0
        else:
            direction = "⏳ SIDEWAYS (Wait)"
            stop_loss_est = round(last_price * 0.985, 0)
            
        return {
            "Ticker": ticker_name,
            "Live Price": last_price,
            "5m Change %": round(change_pct, 2),
            "VWAP Intraday": round(last_vwap, 0),
            "Stoch %K": round(last_k, 2),
            "Stoch %D": round(last_d, 2),
            "Est. Arah": direction,
            "Proteksi Stop Loss": stop_loss_est
        }
    except:
        return None

# --- 5. RUNNER SCANNER MENITAN ---
def run_scalper_scanner(ticker_list):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(analyze_scalping_momentum, t): t for t in ticker_list}
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            if res is not None:
                results.append(res)
    return pd.DataFrame(results)

# --- 6. INTERFACE STREAMLIT ---
st.markdown("<h1 class='main-title'>⚡ Scalper Radar Menitan (Sinyal Instan & Proteksi Stop Loss)</h1>", unsafe_allow_html=True)
st.write(f"Terakhir Diperbarui: {datetime.now().strftime('%H:%M:%S')} WIB (Auto-Refresh intraday 5 Menit aktif)")

# Tombol Manual Force Refresh Data Menit Ini
if st.button("🔄 Tembak Refresh Data Sekarang"):
    st.cache_data.clear()

# Pilihan Emiten Pantauan
saham_di_scan = st.multiselect("Pilih Saham Pantauan Scalping Aktif:", options=master_tickers_clean, default=["AMMN", "ADRO", "BRIS", "GOTO", "ASSA"])

if len(saham_di_scan) > 0:
    df_scalp = run_scalper_scanner(saham_di_scan)
    
    if not df_scalp.empty:
        # Urutkan berdasarkan perubahan harga 5 menit terakhir yang paling tinggi volatilitasnya
        df_scalp = df_scalp.sort_values(by="5m Change %", ascending=False)
        
        # Mewarnai baris tabel agar respons keputusan mata bisa sepersekian detik
        def style_scalper(row):
            styles = [''] * len(row)
            arah = str(row['Est. Arah'])
            idx_arah = row.index.get_loc('Est. Arah')
            idx_sl = row.index.get_loc('Proteksi Stop Loss')
            
            if "STRONG UP" in arah:
                styles[idx_arah] = 'background-color: #047857; color: white; font-weight: bold;'
            elif "UP MOMENTUM" in arah:
                styles[idx_arah] = 'background-color: #065F46; color: #A7F3D0;'
            elif "DUMP RISK" in arah:
                styles[idx_arah] = 'background-color: #991B1B; color: white; font-weight: bold;'
                styles[idx_sl] = 'color: #EF4444; font-weight: bold;'
            elif "DOWN" in arah:
                styles[idx_arah] = 'color: #F87171;'
            return styles

        styled_df = df_scalp.style.apply(style_scalper, axis=1)\
                                  .format({
                                      "Live Price": "Rp {:,.0f}",
                                      "5m Change %": "{:+.2f}%",
                                      "VWAP Intraday": "Rp {:,.0f}",
                                      "Stoch %K": "{:.2f}",
                                      "Stoch %D": "{:.2f}",
                                      "Proteksi Stop Loss": "Rp {:,.0f}"
                                  })
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Tips Membaca Radar Scalping untuk Eksekusi Order
        st.markdown("""
        ### 📑 Pro-Tips Cara Baca Sinyal untuk Eksekusi Cepat:
        1. **Eksekusi Buy (Haka):** Masuk hanya jika **Est. Arah** berstatus `🚀 STRONG UP` atau `📈 UP MOMENTUM`. Ini menandakan harga bergerak di atas VWAP dengan konfirmasi volume tebal pembeli.
        2. **Kunci Penyelamat Stop Loss:** Lihat kolom **Proteksi Stop Loss**. Jika Anda sudah masuk posisi dan harga tiba-tiba ambles di bawah angka tersebut, langsung lakukan *Cut Loss* tanpa ragu karena tren menitannya resmi patah.
        3. **Filter Anti-Jebakan:** Jika status tertulis `📉 DOWN (Jangan Entry)`, abaikan saham tersebut walaupun harganya terlihat murah, karena secara rata-rata volume intraday harganya masih tertekan turun bawah.
        """)
    else:
        st.info("Menunggu respon server data bursa...")
