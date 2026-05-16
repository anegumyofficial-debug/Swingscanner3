import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
import concurrent.futures

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Swing Trading Scanner BEI", layout="wide", page_icon="📈")

# --- 2. CUSTOM CSS (Tampilan Bersih & Profesional) ---
st.markdown("""
    <style>
    .stApp { background-color: #FAFAFA; }
    div[data-testid="stMetricValue"] { font-size: 26px; font-weight: bold; }
    .main-title { color: #1E1E1E; font-weight: 800; padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE SELURUH EMITEN AKTIF INDONESIA (HARDCODED) ---
@st.cache_data(ttl=604800) # Disimpan dalam cache selama 1 minggu agar loading instant
def load_all_indonesia_tickers():
    saham_bei = [
        # --- PERBANKAN & KEUANGAN ---
        "BBCA", "BBRI", "BMRI", "BBNI", "BRIS", "BBTN", "BDMN", "BTPN", "BJBR", "BJTM", 
        "AGRO", "BCIC", "BINA", "DNAR", "MAYB", "MEGA", "PNBN", "PNBS", "BVIC", "BBHI", 
        "ARTO", "BBYB", "BYBK", "BNGA", "BNLI", "BSIM", "NISP", "PNLF", "PANS", "ADMF",
        
        # --- TAMBANG, ENERGI & MINERAL ---
        "ADRO", "PTBA", "ITMG", "HRUM", "INDY", "DOID", "KKGI", "BYAN", "GEMS", "BUMI", 
        "DEWA", "TOBA", "MEDC", "ENRG", "PGAS", "AKRA", "PGEO", "ANTM", "TINS", "INCO", 
        "MDKA", "MBMA", "NCKL", "BRMS", "DKFT", "PSAB", "ZINC", "IFSH", "MBAP", "SGER",
        
        # --- INFRASTRUKTUR, TELEKOMUNIKASI & LOGISTIK ---
        "TLKM", "EXCL", "ISAT", "FREN", "TOWR", "TBIG", "CENT", "JSMR", "BIRD", "SMDR", 
        "TMAS", "ASSA", "META", "CMNP", "POWR", "KEEN", "ARKO", "WEGE", "WIKA", "PTPP", 
        "ADHI", "TOTL", "ACST", "BPII", "BLTA", "GIAA", "NELY", "HAIS", "IPCM",
        
        # --- BARANG KONSUMEN PRIMER (Makanan, Rokok, Kebun) ---
        "INDF", "ICBP", "UNVR", "MYOR", "GGRM", "HMSP", "WIIM", "AALI", "LSIP", "SIMP", 
        "BWPT", "TAPG", "DSNG", "SSMS", "ANDI", "CLEO", "CAMP", "ROTI", "GOOD", "PSSI", 
        "STAA", "TBLA", "SGRO", "SMAR", "CPRO", "JPFA", "CPIN", "MAIN", "WMUU",
        
        # --- BARANG KONSUMEN NON-PRIMER (Ritel, Media, Otomotif) ---
        "ASII", "ACES", "MAPI", "MAPA", "ERA", "RALS", "AMRT", "MEDI", "MNCN", "SCMA", 
        "EMTKM", "LINK", "NETV", "AUTO", "DRMA", "SMSM", "GJTL", "MASA", "IMAS", "LPPF", 
        "PMMP", "PANR", "BUVA", "MDIA", "V擴O", "FORU", "ALTO",
        
        # --- KESEHATAN & FARMASI ---
        "KLBF", "MIKA", "HEAL", "SILO", "SAME", "PRDA", "TSPC", "KAEF", "INAF", "PEHA", 
        "BMHS", "IRRA", "OMED", "SIDO",
        
        # --- PROPERTI & REAL ESTATE ---
        "BSDE", "PWON", "CTRA", "SMRA", "ASRI", "DUTI", "DILD", "PPRO", "LPCK", "LPKR", 
        "MDLN", "BKSL", "KIJA", "BEST", "SSIA", "AMAN", "BAPA", "FMII", "GAMA", "JRPT",
        
        # --- TEKNOLOGI & DIGITAL EKONOMI ---
        "GOTO", "BUKA", "BELI", "WIFI", "ATIC", "HDIT", "MLPT", "MCAS", "DIVA", "KREN", 
        "ASPI", "GLVA", "ZYRX",
        
        # --- PERINDUSTRIAN, KIMIA & MATERIAL DASAR ---
        "AMMN", "JPFA", "MAIN", "SMGR", "INTP", "SMCB", "BRPT", "TPIA", "INKP", "TKIM", 
        "ANJT", "LTLS", "UNIC", "AGII", "ESSA", "TOTO", "AVIA", "MARK", "ALKA"
    ]
    
    cleaned_list = []
    for code in saham_bei:
        c_clean = str(code).strip().upper()
        if not c_clean.endswith(".JK"):
            c_clean = f"{c_clean}.JK"
        cleaned_list.append(c_clean)
        
    return sorted(list(set(cleaned_list)))

master_tickers_jk = load_all_indonesia_tickers()
master_tickers_clean = [t.replace(".JK", "") for t in master_tickers_jk]

# --- 4. DATA CLEANING UTILITY ---
def clean_yf_dataframe(df):
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)
    return df

# --- 5. SATUAN FUNGSI SCANNING PER SAHAM (UNTUK PARALEL/MULTI-THREADING) ---
def fetch_and_analyze_stock(ticker):
    try:
        formatted_ticker = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
        df = yf.download(formatted_ticker, period="6mo", interval="1d", progress=False)
        df = clean_yf_dataframe(df)
        
        if df is None or len(df) < 35: 
            return None
        
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        last_price = float(df['Close'].iloc[-1])
        prev_price = float(df['Close'].iloc[-2])
        change_pct = ((last_price - prev_price) / prev_price) * 100
        
        last_rsi = float(df['RSI'].iloc[-1])
        last_ma20 = float(df['MA20'].iloc[-1])
        last_ma50 = float(df['MA50'].iloc[-1])
        prev_ma20 = float(df['MA20'].iloc[-2])
        
        trend = "Up-Trend" if last_price > last_ma50 else "Down-Trend"
        
        if last_rsi < 35:
            action = "BUY (Oversold)"
        elif last_price > last_ma20 and prev_price <= prev_ma20:
            action = "BUY (MA Cross)"
        elif last_rsi > 70:
            action = "SELL (Overbought)"
        else:
            action = "Wait/Neutral"
        
        return {
            "Ticker": ticker.replace(".JK", ""),
            "Price": last_price,
            "Change %": round(change_pct, 2),
            "RSI": round(last_rsi, 2),
            "Trend": trend,
            "Actionable": action
        }
    except:
        return None

# --- 6. CORE BULK SCANNER DENGAN MULTI-THREADING ---
@st.cache_data(ttl=900) 
def run_bulk_scanner(ticker_list):
    results = []
    # Menggunakan max_workers=15 agar loading cepat namun terhindar dari IP Banned oleh Yahoo Finance
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_ticker = {executor.submit(fetch_and_analyze_stock, t): t for t in ticker_list}
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            if res is not None:
                results.append(res)
    return pd.DataFrame(results)

# --- 7. GRAPH FETCHING (SINGLE STOCK DETAIL ANALYSIS) ---
@st.cache_data(ttl=300)
def get_single_stock_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        df = clean_yf_dataframe(df)
        if df is None or len(df) < 20:
            return None
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        return df
    except:
        return None

# --- 8. TAMPILAN UTAMA & NAVIGATION ---
st.markdown("<h1 class='main-title'>📈 Swing Trading Dashboard (Seluruh Saham BEI)</h1>", unsafe_allow_html=True)

# --- 9. SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    st.subheader("🌐 Saring Kelompok Scanner")
    pilihan_mode = st.radio(
        "Pilih Cakupan Emiten:", 
        ["Saham Pilihan Utama (LQ45/Bluechip)", "Kustom Pilih Sendiri (Multi-Select)", "Scan Berdasarkan Kelompok Abjad"]
    )
    
    if pilihan_mode == "Saham Pilihan Utama (LQ45/Bluechip)":
        saham_di_scan = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "GOTO", "UNVR", "ADRO", "PTBA", "BRIS", "ANTM", "INDF", "ICBP", "KLBF", "AMMN", "MDKA", "SIDO"]
    elif pilihan_mode == "Kustom Pilih Sendiri (Multi-Select)":
        saham_di_scan = st.multiselect(
            "Ketik & Pilih Kode Saham BEI Anda:", 
            options=master_tickers_clean, 
            default=["BBCA", "BBRI", "BMRI", "BBNI", "TLKM"]
        )
    else:
        kelompok_abjad = st.selectbox("Pilih Urutan Abjad
