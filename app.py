import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
import concurrent.futures
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Swing Trading Scanner BEI", layout="wide", page_icon="📈")

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #FAFAFA; }
    div[data-testid="stMetricValue"] { font-size: 26px; font-weight: bold; }
    .main-title { color: #1E1E1E; font-weight: 800; padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE EMITEN BEI RAKSASA ---
@st.cache_data(ttl=604800)
def load_all_indonesia_tickers():
    saham_bei = [
        # --- PERBANKAN & KEUANGAN ---
        "BBCA", "BBRI", "BMRI", "BBNI", "BRIS", "BBTN", "BDMN", "BTPN", "BJBR", "BJTM", 
        "AGRO", "BCIC", "BINA", "DNAR", "MAYB", "MEGA", "PNBN", "PNBS", "BVIC", "BBHI", 
        "ARTO", "BBYB", "BYBK", "BNGA", "BNLI", "BSIM", "NISP", "PNLF", "PANS", "ADMF",
        "BCAP", "BBLD", "BABP", "BACA", "BESS", "CFIN", "DEFI", "GSMF", "MASB", "NOBU",
        
        # --- TAMBANG, ENERGI & MINERAL ---
        "AADI", "ADRO", "PTBA", "ITMG", "HRUM", "INDY", "DOID", "KKGI", "BYAN", "GEMS", 
        "BUMI", "DEWA", "TOBA", "MEDC", "ENRG", "PGAS", "AKRA", "PGEO", "ANTM", "TINS", 
        "INCO", "MDKA", "MBMA", "NCKL", "BRMS", "DKFT", "PSAB", "ZINC", "IFSH", "MBAP", 
        "SGER", "DSSA", "ELPI", "APEX", "ARTI", "BIPI", "BOSS", "CTTH", "CUAN",
        "GREN", "IATA", "MDVS", "MITI", "PKPK", "RMKO", "RMKE", "SURE", "WOWS",
        
        # --- INFRASTRUKTUR, TELEKOMUNIKASI & LOGISTIK ---
        "MORA", "TLKM", "EXCL", "ISAT", "FREN", "TOWR", "TBIG", "CENT", "JSMR", "BIRD", 
        "SMDR", "TMAS", "ASSA", "META", "CMNP", "POWR", "KEEN", "ARKO", "WEGE", "WIKA", 
        "PTPP", "ADHI", "TOTL", "ACST", "BPII", "BLTA", "GIAA", "NELY", "HAIS", "IPCM",
        "BALI", "BUKK", "CASS", "GHON", "GIPH", "HITS", "IBST", "JAST", "LINK", "PORT",
        
        # --- BARANG KONSUMEN PRIMER ---
        "CMRY", "INDF", "ICBP", "UNVR", "MYOR", "GGRM", "HMSP", "WIIM", "AALI", "LSIP", 
        "SIMP", "BWPT", "TAPG", "DSNG", "SSMS", "CLEO", "CAMP", "ROTI", "GOOD", "PSSI", 
        "STAA", "TBLA", "SGRO", "SMAR", "CPRO", "JPFA", "CPIN", "MAIN", "WMUU", "AISA",
        "ALTO", "BISI", "BTEK", "BUDI", "CEKA", "DLTA", "FOOD", "IKAN", "KEJU", "PANI",
        
        # --- BARANG KONSUMEN NON-PRIMER ---
        "ASII", "ACES", "MAPI", "MAPA", "ERAA", "RALS", "AMRT", "MEDI", "MNCN", "SCMA", 
        "EMTK", "NETV", "AUTO", "DRMA", "SMSM", "GJTL", "MASA", "IMAS", "LPPF", "CBDK",
        "PMMP", "PANR", "BUVA", "MDIA", "FORU", "AGAR", "AMMS", "BABY", "BELI", "BIPN", 
        "CARS", "EPAC", "FILM", "GLOB", "HOME", "HOTL", "IKBI", "KBLA", "LPIN", "MSIN",
        
        # --- KESEHATAN & FARMASI ---
        "KLBF", "MIKA", "HEAL", "SILO", "SAME", "PRDA", "TSPC", "KAEF", "INAF", "PEHA", 
        "BMHS", "IRRA", "OMED", "SIDO", "ASTA", "CARE", "DGNS", "MREI", "PRIM", "SOCI",
        
        # --- PROPERTI & REAL ESTATE ---
        "BSDE", "PWON", "CTRA", "SMRA", "ASRI", "DUTI", "DILD", "PPRO", "LPCK", "LPKR", 
        "MDLN", "BKSL", "KIJA", "BEST", "SSIA", "AMAN", "BAPA", "FMII", "JRPT",
        "ADMG", "AMOR", "APLN", "BIPP", "COCO", "CPRI", "DMAS", "EMDE", "GURA",
        
        # --- TEKNOLOGI & DIGITAL EKONOMI ---
        "GOTO", "BUKA", "WIFI", "ATIC", "HDIT", "MLPT", "MCAS", "DIVA", "ASPI", "GLVA", 
        "ZYRX", "AWAN", "BTEL", "CHIP", "CYBR", "KREN", "LUCK", "PTMP", "SKYB",
        
        # --- PERINDUSTRIAN, KIMIA & MATERIAL DASAR ---
        "AMMN", "SMGR", "INTP", "BRPT", "TPIA", "INKP", "TKIM", "ANJT", "LTLS", "UNIC", 
        "AGII", "ESSA", "TOTO", "AVIA", "MARK", "ALKA", "AKPI", "ALMI", "BAJA", "BRAM", 
        "BRNA", "GDST", "IGAR", "IMPC", "INAI", "INCI", "KRAS", "LION", "LMSH", "NIKL"
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
    
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    df.index = pd.to_datetime(df.index)
    return df

# --- 5. DETEKSI INDIVIDUAL STOCK ---
def fetch_and_analyze_stock(ticker):
    try:
        formatted_ticker = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
        df = yf.download(formatted_ticker, period="6mo", interval="1d", progress=False)
        df = clean_yf_dataframe(df)
        
        if df is None or len(df) < 35 or 'Close' not in df.columns: 
            return None
        
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        last_price = float(df['Close'].iloc[-1])
        prev_price = float(df['Close'].iloc[-2])
        change_pct = ((last_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0.0
        
        last_volume = float(df['Volume'].iloc[-1]) if 'Volume' in df.columns and not pd.isna(df['Volume'].iloc[-1]) else 0.0
        
        raw_ma20 = df['MA20'].iloc[-1]
        last_ma20 = float(raw_ma20) if not pd.isna(raw_ma20) else last_price
        
        raw_ma50 = df['MA50'].iloc[-1]
        last_ma50 = float(raw_ma50) if not pd.isna(raw_ma50) else last_price
        
        raw_rsi = df['RSI'].iloc[-1]
        last_rsi = float(raw_rsi) if not pd.isna(raw_rsi) else 50.0
        
        prev_ma20_raw = df['MA20'].iloc[-2]
        prev_ma20_val = float(prev_ma20_raw) if not pd.isna(prev_ma20_raw) else prev_price
        
        trend = "Up-Trend" if last_price > last_ma50 else "Down-Trend"
        
        if last_price > last_ma20 and last_price > last_ma50:
            keterangan = "Diatas MA20 & MA50 (Strong)"
        elif last_
