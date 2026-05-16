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
        "BRNA", "GDST", "IGAR", "IMPC",
