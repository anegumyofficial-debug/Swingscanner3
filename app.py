import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import concurrent.futures

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Scalper Radar BEI - Full Edition", layout="wide", page_icon="⚡")

# --- 2. CUSTOM CSS SCALPER ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #F8FAFC; }
    .main-title { color: #38BDF8; font-weight: 800; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE EMITEN UTUH DAN LENGKAP (80+ EMITEN BEI) ---
@st.cache_data(ttl=604800)
def load_all_market_tickers():
    saham_lengkap = [
        "AADI", "AALI", "ABBA", "ABDA", "ABMM", "ACES", "ACST", "ADCP", "ADHI", "ADME",
        "ADRO", "AKRA", "AMMN", "AMRT", "ANTM", "APEX", "ARNA", "ARTO", "ASII", "ASRI", 
        "ASSA", "AUTO", "AVIA", "BBCA", "BBNI", "BBRI", "BBTN", "BBYB", "BCIC", "BDMN",
        "BFIN", "BGTG", "BIPP", "BKSL", "BMRI", "BMTR", "BNGA", "BNLI", "BRMS", "BRIS",
        "BSDE", "BTEK", "BTPS", "BUMI", "BUVA", "CARS", "CENT", "CINT", "CLEO", "CMNP",
        "CNTX", "CPIN", "CTRA", "DIGI", "DILD", "DLTA", "DMMX", "DMAS", "DOOH", "ELSA",
        "EMTK", "ENRG", "EXCL", "FAST", "FILM", "FORU", "FPNI", "GARA", "GDST", "GGRM",
        "GIAA", "GJTL", "GOTO", "GPSO", "HDFA", "HEAL", "HISP", "HMPA", "HMSP", "HRUM",
        "IATA", "INCF", "INDF", "INDY", "INKP", "INTP", "ISAT", "ITMG", "KAEF", "KIJA",
        "KLBF", "KPIG", "KREN", "LANC", "LPKR", "LPPF", "MAPI", "MDKA", "MEDC", "MLPL",
        "MNCN", "MPPA", "MYOR", "NATO", "NZIA", "OASA", "PANS", "PBRX", "PGAS", "PGJO",
        "PNBS", "PNLF", "PTBA", "PTPP", "PWON", "RMKO", "SCMA", "SIDO", "SMGR", "SMRA",
        "SRTG", "SSMS", "TINS", "TLKM", "TOWR", "TPIA", "UNTR", "UNVR", "VKTR", "WIKA"
    ]
    return sorted([f"{t}.JK" for t in saham_lengkap])

master_tickers_jk = load_all_market_tickers()
master_tickers_clean = [t.replace(".JK", "") for t in master_tickers_jk]

def clean_yf_dataframe(df):
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df

# --- 4. ENGINE ANALISIS INTERDAY SCALPING & VALIDASI FILTER ---
def analyze_scalping_momentum(ticker):
    try:
        formatted_ticker = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
        
        # Mode Utama: Coba ambil data intraday 5 menit terlebih dahulu
        df = yf.download(formatted_ticker, period="3d", interval="5m", progress=False)
        df = clean_yf_dataframe(df)
        is_fallback = False
        
        # Mode Cadangan: Jika di malam hari data 5m kosong, beralih ke data harian agar tidak eror
        if df is None or len(df) < 15 or 'Close' not in df.columns:
            df = yf.download(formatted_ticker, period="3mo", interval="1d", progress=False)
            df = clean_yf_dataframe(df)
            is_fallback = True
            
        if df is None or len(df) < 15 or 'Close' not in df.columns: 
            return None
        
        # Perhitungan Indikator Jalur VWAP / MA Cadangan
        if not is_fallback:
            cum_vol = df['Volume'].cumsum()
            cum_vol_price = (df['Close'] * df['Volume']).cumsum()
            df['VWAP'] = cum_vol_price / cum_vol
        else:
            # Di mode harian malam hari, VWAP digantikan perannya oleh EMA20 historis
            df['VWAP'] = ta.ema(df['Close'], length=20)
        
        # Stochastic Oscillator Cepat
        stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
        df['STOCHk'] = stoch['STOCHk_14_3_3']
        df['STOCHd'] = stoch['STOCHd_14_3_3']
        
        df['EMA9'] = ta.ema(df['Close'], length=9)
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        total_turnover_today = (df['Close'] * df['Volume']).sum()
        
        # Data Menit/Hari Terakhir
        last_price = float(df['Close'].iloc[-1])
        last_vwap = float(df['VWAP'].iloc[-1]) if not pd.isna(df['VWAP'].iloc[-1]) else last_price
        last_k = float(df['STOCHk'].iloc[-1]) if not pd.isna(df['STOCHk'].iloc[-1]) else 50.0
        last_d = float(df['STOCHd'].iloc[-1]) if not pd.isna(df['STOCHd'].iloc[-1]) else 50.0
        last_ema = float(df['EMA9'].iloc[-1]) if not pd.isna(df['EMA9'].iloc[-1]) else last_price
        last_volume = float(df['Volume'].iloc[-1])
        last_vol_ma = float(df['Vol_MA20'].iloc[-1]) if not pd.isna(df['Vol_MA20'].iloc[-1]) else 1.0
        
        prev_price = float(df['Close'].iloc[-2])
        change_pct = ((last_price - prev_price) / prev_price) * 100
        
        ticker_name = ticker.replace(".JK", "")
        
        # Penilaian Validitas Volume dan Likuiditas
        is_volume_spike = last_volume > (last_vol_ma * 1.3)
        is_highly_liquid = total_turnover_today > 3_000_000_000  # Threshold disesuaikan ke 3B untuk fleksibilitas waktu luar bursa
        
        # LOGIKA ESTIMASI ARAH, STOP LOSS, & TAKE PROFIT
        if last_price > last_vwap and last_price > last_ema and last_k > last_d and last_k < 50:
            if is_volume_spike and is_highly_liquid:
                direction = "🚀 STRONG UP (Siap Buy)"
            else:
                direction = "📈 UP MOMENTUM (Koleksi)"
                
            stop_loss_est = round(min(last_vwap, last_ema), 0)
            risk_distance = max(last_price - stop_loss_est, last_price * 0.01)
            take_profit_est = round(last_price + (risk_distance * 1.5), 0)
            
        elif last_price > last_vwap and last_k > last_d:
            direction = "📈 UP MOMENTUM (Koleksi)"
            stop_loss_est = round(last_vwap, 0)
            risk_distance = max(last_price - stop_loss_est, last_price * 0.01)
            take_profit_est = round(last_price + (risk_distance * 1.5), 0)
            
        elif last_price < last_ema and last_k < last_d and last_k > 65:
            direction = "🚨 DUMP RISK (Jangan Haka)"
            stop_loss_est = round(last_price * 0.99, 0)
            take_profit_est = 0
            
        elif last_price < last_vwap:
            direction = "📉 DOWN (Hindari)"
            stop_loss_est = 0
            take_profit_est = 0
        else:
            direction = "⏳ SIDEWAYS (Wait)"
            stop_loss_est = round(last_price * 0.99, 0)
            take_profit_est = round(last_price * 1.02, 0)
            
        # Catatan Penanda jika data beralih ke mode penutupan harian
        if is_fallback:
            direction += " [Hari Kemarin]"
            
        return {
            "Ticker": ticker_name,
            "Live Price": last_price,
            "Change %": round(change_pct, 2),
            "Turnover (B)": round(total_turnover_today / 1_000_000_000, 2),
            "VWAP/MA Baseline": round(last_vwap, 0),
            "Stoch %K": round(last_k, 2),
            "Stoch %D": round(last_d, 2),
            "Est. Arah": direction,
            "Proteksi Stop Loss": stop_loss_est,
            "Estimasi Take Profit": take_profit_est
        }
    except:
        return None

def run_scalper_scanner(ticker_list):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_ticker = {executor.submit(analyze_scalping_momentum, t): t for t in ticker_list}
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            if res is not None:
                results.append(res)
    return pd.DataFrame(results)

# --- 5. INTERFACE PANEL KONTROL & SIDEBAR ---
st.markdown("<h1 class='main-title'>⚡ Scalper Radar Pro (Sinyal Siap Buy & Target TP/SL)</h1>", unsafe_allow_html=True)

col_title1, col_title2 = st.columns(2)
with col_title1:
    st.write(f"Terakhir Sinkron: {datetime.now().strftime('%H:%M:%S')} WIB")
with col_title2:
    if st.button("🔄 Tembak Refresh Data", use_container_width=True):
        st.cache_data.clear()

with st.sidebar:
    st.header("⚙️ Filter Validasi Pasar")
    only_ready_to_buy = st.checkbox("🎯 Hanya Tampilkan Sinyal SIAP BUY", value=False)
    st.markdown("---")
    saham_pilihan = st.multiselect(
        "Pilih Emiten Pantauan:", 
        options=master_tickers_clean, 
        default=["AMMN", "ADRO", "BRIS", "GOTO", "ASSA", "APEX", "ARNA", "ACES"]
    )

if len(saham_pilihan) > 0:
    df_scalp = run_scalper_scanner(saham_pilihan)
    
    if not df_scalp.empty:
        if only_ready_to_buy:
            df_scalp = df_scalp[df_scalp["Est. Arah"].str.contains("STRONG UP|UP MOMENTUM")]
        
        df_scalp = df_scalp.sort_values(by="Change %", ascending=False)
        
        def style_scalper(row):
            styles = [''] * len(row)
            arah = str(row['Est. Arah'])
            idx_arah = row.index.get_loc('Est. Arah')
            idx_sl = row.index.get_loc('Proteksi Stop Loss')
            idx_tp = row.index.get_loc('Estimasi Take Profit')
            
            if "STRONG UP" in arah:
                styles[idx_arah] = 'background-color: #047857; color: white; font-weight: bold;'
                styles[idx_tp] = 'color: #34D399; font-weight: bold;'
            elif "UP MOMENTUM" in arah:
                styles[idx_arah] = 'background-color: #065F46; color: #A7F3D0;'
                styles[idx_tp] = 'color: #34D399;'
            elif "DUMP RISK" in arah:
                styles[idx_arah] = 'background-color: #991B1B; color: white; font-weight: bold;'
                styles[idx_sl] = 'color: #F87171; font-weight: bold;'
            return styles

        if not df_scalp.empty:
            styled_df = df_scalp.style.apply(style_scalper, axis=1)\
                                      .format({
                                          "Live Price": "Rp {:,.0f}",
                                          "Change %": "{:+.2f}%",
                                          "Turnover (B)": "{:,.2f} B",
                                          "VWAP/MA Baseline": "Rp {:,.0f}",
                                          "Stoch %K": "{:.2f}",
                                          "Stoch %D": "{:.2f}",
                                          "Proteksi Stop Loss": "Rp {:,.0f}",
                                          "Estimasi Take Profit": "Rp {:,.0f}"
                                      })
            
            st.dataframe(styled_df, use_container_width=True, height=450)
        else:
            st.warning("⚠️ Tidak ada emiten yang lolos filter validasi ketat 'Siap Buy' saat ini.")
            
        st.markdown("""
        ### 💡 Aturan Pembacaan Dashboard Adaptif:
        * **[Hari Kemarin]:** Jika tanda ini muncul di kolom arah, artinya bursa sedang tutup/data menitan kosong, dan dashboard otomatis menampilkan data penutupan hari bursa terakhir agar Anda tetap bisa melakukan analisis malam hari.
        * **Turnover (B):** Mengukur nilai transaksi riil dalam satuan Miliar Rupiah untuk menyaring pergerakan palsu bandar lokal.
        """)
    else:
        st.error("Gagal menarik data pasar dari Yahoo Finance. Silakan coba tekan tombol refresh di atas beberapa saat lagi.")
