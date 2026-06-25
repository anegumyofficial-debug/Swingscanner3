import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import pytz  
import concurrent.futures

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Scalper Radar BEI - Full Edition", layout="wide", page_icon="⚡")

# Mengunci jam server ke zona waktu WIB (Asia/Jakarta)
wib_tz = pytz.timezone('Asia/Jakarta')
wib_now = datetime.now(wib_tz)

# --- 2. CUSTOM CSS SCALPER ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #F8FAFC; }
    .main-title { color: #38BDF8; font-weight: 800; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)


# --- 3. DATABASE MASTER EMITEN ---
@st.cache_data(ttl=604800)
def load_mega_market_tickers():
    saham_300_plus = [
        "AADI", "AALI", "ABBA", "ABDA", "ABMM", "ACES", "ACST", "ADCP", "ADHI", "ADME", "ADRO", "AGRO", "AGRS", "AHAP", "AISA",
        "AKRA", "AKSI", "ALDO", "ALKA", "ALMI", "AMAG", "AMAN", "AMAR", "AMMN", "AMOR", "AMRT", "ANDI", "ANER", "ANTM", "APEX",
        "APII", "APLN", "ARGO", "ARII", "ARKA", "ARNA", "ARTA", "ARTO", "ASBI", "ASGR", "ASII", "ASJT", "ASMI", "ASPI", "ASRI",
        "ASSA", "ATAP", "ATIC", "AUTO", "AVIA", "AWAN", "AYAM", "BADI", "BAJA", "BALI", "BANK", "BAPA", "BAPP", "BARA", "BATA",
        "BAUT", "BBCA", "BBHI", "BBIK", "BBLD", "BBMD", "BBNI", "BBRI", "BBRM", "BBTN", "BBUV", "BBYB", "BCIC", "BCIP", "BDMN",
        "BEEF", "BEKS", "BFIN", "BFTC", "BGTG", "BHAT", "BHIT", "BIMA", "BIPI", "BIPP", "BIRD", "BISI", "BKDP", "BKSL", "BKSW",
        "BMAS", "BMBL", "BMRI", "BMTR", "BNGA", "BNLI", "BNII", "BOBA", "BOLA", "BORO", "BPII", "BRMS", "BRIS", "BRNA", "BRPT",
        "BSDE", "BSIM", "BSSR", "BSWD", "BTEK", "BTPS", "BUKK", "BUVA", "BUMI", "BUTI", "BVIC", "BWPT", "BYAN", "CADI", "CAMP",
        "CANT", "CARE", "CARS", "CASA", "CASH", "CASS", "CATT", "CBDK", "CEKA", "CENT", "CESS", "CFIN", "CINT", "CITA", "CITY", 
        "CLAY", "CLEO", "CLPI", "CMNP", "CMRY", "CNMA", "CNTX", "COAL", "COCO", "CPIN", "CPRI", "CPRO", "CSAP", "CSIS", "CSRA", 
        "CTRA", "CTTH", "CUAN", "CYBER", "DAAZ", "DART", "DAYA", "DEAL", "DEFI", "DEWA", "DFAM", "DGIK", "DHCO", "DIGI", "DILD", 
        "DIVA", "DKFT", "DLTA", "DMAS", "DMED", "DMMX", "DNAR", "DOMI", "DOOH", "DPNS", "DPUM", "DRMA", "DSSA", "DSFI", "DSNG", 
        "DTAL", "DUTO", "DVLA", "DXJN", "DYAN", "EAST", "ECII", "EDII", "EKAD", "ELIT", "ELSA", "EMAL", "EMDE", "EMTK", "ENRG", 
        "EPAC", "EPMT", "ERAA", "ERTX", "ESIP", "ESSA", "ESTA", "ETWA", "EXCL", "FAPA", "FAST", "FASW", "FEST", "FIKA", "FILM", 
        "FINN", "FIRE", "FMII", "FPNI", "FORU", "FOTA", "FRAS", "FUJI", "GAMA", "GAMR", "GARA", "GCOAL", "GDST", "GDYR", "GEMS", 
        "GGRM", "GHEO", "GIAA", "GJTL", "GLOB", "GMCW", "GMTD", "GOLD", "GOTO", "GPRA", "GPSO", "GRHA", "GRIA", "GRPM", "GSMF", 
        "GSJA", "GTBO", "HAIS", "HAKA", "HAMP", "HDFA", "HDIT", "HEAL", "HELI", "HERO", "HEXA", "HIKAM", "HINT", "HISP", "HKMU", 
        "HLIT", "HMAI", "HMPA", "HMSP", "HOKI", "HOMI", "HOTL", "HRTA", "HRUM", "IATA", "IBOS", "IBST", "ICBP", "ICON", "IDPR", 
        "IKAN", "IKBI", "IKHA", "IMAS", "IMJS", "IMPC", "INAF", "INCF", "INDF", "INDO", "INDX", "INDY", "INKP", "INPC", "INPP", 
        "INPS", "INRU", "INTA", "INTD", "INTP", "IPAC", "IPCC", "IPCM", "IPOL", "IRRA", "ISAT", "ISSP", "ITMA", "ITMG", "JAWA", 
        "JECC", "JGLE", "JIHD", "JKON", "JKSW", "JMAS", "JPFA", "JRPT", "JSKY", "JSMR", "JSTB", "JTPE", "KAEF", "KICI", "KIJA", 
        "KKGI", "KLBF", "KLAS", "KMDS", "KOBX", "KOIN", "KOKA", "KOTA", "KPAL", "KPAS", "KPIG", "KREN", "KRNA", "KRAS", "KRAH", 
        "KREI", "LION", "LPCK", "LPKR", "LPLI", "LPPF", "LPPS", "LRN",  "LSIP", "LTLS", "LUCK", "LUMI", "MAIN", "MAMI", "MAPA", 
        "MAPI", "MARI", "MARK", "MASA", "MAYA", "MBAP", "MBSS", "MBTO", "MCOL", "MDIA", "MDKA", "MDKI", "MDLN", "MEDC", "MEGA", 
        "MERK", "META", "MFIN", "MGNA", "MHAX", "MICE", "MIDI", "MILA", "MINA", "MINK", "MIRA", "MITI", "MKNT", "MKPI", "MLBI", 
        "MLIA", "MLPL", "MLPT", "MMIX", "MNCN", "MPMX", "MPPA", "MRAT", "MRPK", "MSIN", "MSKY", "MTDL", "MTEL", "MTFN", "MTLA", 
        "MTMH", "MTPS", "MTRA", "MTSM", "MUTU", "MYOH", "MYOR", "MYTX", "NANO", "NASA", "NASI", "NATO", "NAIK", "NBHA", "NELY", 
        "NETV", "NFCX", "NICK", "NICL", "NIRO", "NISP", "NMSL", "NOBU", "NRCA", "NREI", "NTBK", "NUSA", "NVOM", "NZIA", "OASA", 
        "OBMD", "ODEC", "OILS", "OKAS", "OMRE", "OPMS", "PADI", "PALM", "PAMA", "PANB", "PANI", "PANR", "PANS", "PBID", "PBRX", 
        "PBSA", "PCAR", "PDES", "PEGE", "PEHA", "PGAS", "PGJO", "PGLI", "PICO", "PIHA", "PMMP", "PMJS", "PNBS", "PNIN", "PNLF", 
        "PNSE", "POLY", "POOL", "PORT", "POWR", "PPRI", "PPRE", "PPRO", "PRAS", "PRDA", "PRIM", "PRST", "PSAB", "PSDN", "PSGO", 
        "PSSI", "PTBA", "PTDU", "PTIS", "PUDP", "PURA", "PURE", "PURI", "PWON", "PYFA", "RAAM", "RACY", "RAFI", "RAJA", "RALS", 
        "RANC", "RBMS", "RCCC", "RELI", "REMD", "RICY", "RIGS", "RIMO", "RMKO", "ROCK", "RODA", "ROTI", "SAGE", "SAIP", "SAME", 
        "SAMF", "SATU", "SBAT", "SCCO", "SCMA", "SCNP", "SDMU", "SDPC", "SDRA", "SEMA", "SFAN", "SGER", "SGIK", "SGRO", "SHID", 
        "SIAP", "SICO", "SIDO", "SILO", "SIMA", "SIMP", "SINI", "SIPD", "SKBM", "SKLT", "SMAR", "SMBR", "SMCB", "SMDM", "SMDR", 
        "SMGR", "SMIL", "SMKM", "SMMA", "SMRA", "SMRU", "SMSM", "SNLK", "SOCI", "SOFE", "SOHO", "SONA", "SPMA", "SPTO", "SRSN", 
        "SRTG", "SSIA", "SSMS", "SSTM", "STAR", "STAA", "SUGI", "SULI", "SUPR", "SURE", "SURYA", "SUSU", "TAIS", "TAMU", "TAMP", 
        "TAPG", "TARA", "TAXI", "TBIG", "TBMS", "TCID", "TCPI", "TEBE", "TECH", "TELE", "TENI", "TFAS", "TFCO", "TGKA", "TGRA", 
        "TIFA", "TINS", "TIRA", "TIRT", "TKIM", "TLKM", "TLDN", "TMAS", "TMPO", "TOBA", "TOGA", "TONS", "TOTAL", "TOTO", "TOWR", 
        "TPIA", "TPMA", "TRAM", "TRIL", "TRIM", "TRIN", "TRIS", "TRJA", "TRJU", "TRST", "TRUE", "TRUK", "TSPC", "TUGU", "TURN", 
        "TYRE", "UCID", "UDNG", "UFOE", "UNGO", "UNIT", "UNTR", "UNVR", "URBN", "UTAA", "VINS", "VIVA", "VIVM", "VKTR", "VOKS", 
        "VONE", "VPAC", "WAPO", "WEGE", "WEHA", "WICO", "WIFI", "WIIM", "WIKA", "WINS", "WIRG", "WITA", "WMUU", "WOOD", "WOWS", 
        "WSBP", "WSKT", "WTG",  "WTIA", "YPAS", "YUASA", "YULE", "ZATA", "ZBRA", "ZINC", "ZONE", "PTRO", "BRAM", "IRSX", "WIFI", "KLBV","NCKL","BELI","ULTJ", "TMPO","DSSA","MDKA","RMKO","RMKE"
    ]
    return sorted(list(set([f"{t.strip().upper()}.JK" for t in saham_300_plus])))

master_tickers_jk = load_mega_market_tickers()
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

@st.cache_data(ttl=300) # Update setiap 5 menit
def get_ihsg_sentiment():
    try:
        ihsg = yf.download("^JKSE", period="5d", progress=False)
        ihsg = clean_yf_dataframe(ihsg)
        last_close = ihsg['Close'].iloc[-1]
        prev_close = ihsg['Close'].iloc[-2]
        trend = (last_close - prev_close) / prev_close * 100
        
        if trend > 0.1:
            return "BULLISH 🟢", "#22C55E"
        elif trend < -0.1:
            return "BEARISH 🔴", "#EF4444"
        else:
            return "SIDEWAYS 🟡", "#EAB308"
    except:
        return "NEUTRAL ⚪", "#94A3B8"
        
def analyze_scalping_momentum(ticker):
    try:
        formatted_ticker = ticker if ticker.endswith(".JK") else f"{ticker}.JK"

        # 1. DOWNLOAD DATA DULU
        df = yf.download(formatted_ticker, period="3d", interval="5m", progress=False)
        df = clean_yf_dataframe(df)
        is_fallback = False
        
        # 2. PENANGANAN FALLBACK (JIKA DATA 5M KOSONG)
        if df is None or len(df) < 15 or 'Close' not in df.columns:
            df = yf.download(formatted_ticker, period="3mo", interval="1d", progress=False)
            df = clean_yf_dataframe(df)
            is_fallback = True
            
        if df is None or len(df) < 15 or 'Close' not in df.columns: 
            return None
        
        # 3. BARU HITUNG INDIKATOR (RSI, VWAP, STOCH, DLL) SETELAH DF VALID
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        if not is_fallback:
            cum_vol = df['Volume'].cumsum()
            cum_vol_price = (df['Close'] * df['Volume']).cumsum()
            df['VWAP'] = cum_vol_price / cum_vol
        else:
            df['VWAP'] = ta.ema(df['Close'], length=20)
        
        # Lanjutkan sisa kode perhitungan lainnya...
        stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
        # ... (sisanya sama seperti kode Anda)
        
        # Pastikan last_rsi diambil di sini
        last_rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50.0
        
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

        # Logika Arah & Momentum
        if last_price > last_vwap and last_k > last_d and last_k < 50:
            direction = "🚀 STRONG UP (Siap Buy)"
            status_sinyal = "BUY"
        elif last_price > last_vwap and last_k > last_d:
            direction = "📈 UP MOMENTUM (Koleksi)"
            status_sinyal = "HOLD"
        elif last_k < last_d and last_k > 65:
            direction = "🚨 DUMP RISK"
            status_sinyal = "SELL"
        else:
            direction = "⏳ SIDEWAYS"
            status_sinyal = "WAIT"

        # Analisis Momentum
        if last_k > 80: momentum = "🔥 Overbought"
        elif last_k < 20: momentum = "🧊 Oversold"
        elif last_k > last_d: momentum = "📈 Bullish"
        else: momentum = "📉 Bearish"

        # --- ESTIMASI DATA ASING (PROKSI STATISTIK) ---
        # Mengambil data 5 hari untuk rata-rata
        df_5d = yf.download(formatted_ticker, period="5d", interval="1d", progress=False)
        df_5d = clean_yf_dataframe(df_5d)
        
        # Proksi: Asumsi 35% dari volume adalah transaksi asing
        avg_vol_5d = df_5d['Volume'].mean()
        last_vol = float(df['Volume'].iloc[-1])
        
        est_foreign_buy = last_vol * 0.35 * 0.52  # 52% dari porsi asing adalah buy saat tren naik
        est_foreign_sell = last_vol * 0.35 * 0.48 # 48% dari porsi asing adalah sell
        net_foreign_val = est_foreign_buy - est_foreign_sell
        
        # Net Foreign Average (5 hari)
        net_foreign_avg = (df_5d['Volume'] * 0.35 * 0.04).mean() # Estimasi rata-rata net 4% dari volume
        
        # --- LOGIKA PERSENTASE DANA ---
        total_pressure = est_foreign_buy + est_foreign_sell
        dana_masuk_pct = round((est_foreign_buy / total_pressure) * 100, 1)
        dana_keluar_pct = round((est_foreign_sell / total_pressure) * 100, 1)


        # ... (di bawah bagian perhitungan Net Foreign)
        net_foreign_val = est_foreign_buy - est_foreign_sell
        
        # Logika Kategori Inst Flow
        turnover_val = total_turnover_today / 1_000_000_000
        if net_foreign_val > (turnover_val * 0.2):
            inst_flow = "Big Accum 🟢"
        elif net_foreign_val > (turnover_val * 0.05):
            inst_flow = "Small Accum 🟡"
        elif net_foreign_val < -(turnover_val * 0.2):
            inst_flow = "Big Dist 🔴"
        elif net_foreign_val < -(turnover_val * 0.05):
            inst_flow = "Small Dist ⚪"
        else:
            inst_flow = "Neutral"
            
        # --- LOGIKA VOLUME TRANSPARAN ---
        # Mengukur tren volume 5 periode terakhir
        vol_trend = df['Volume'].rolling(window=5).mean()
        last_vol = float(df['Volume'].iloc[-1])
        prev_vol = float(df['Volume'].iloc[-2])
        
        # Penentuan Status Volume (Transparan)
        if last_vol > prev_vol * 1.1:
            vol_status = "🟢 Naik (Akumulasi)"
        elif last_vol < prev_vol * 0.9:
            vol_status = "🔴 Turun (Distribusi)"
        else:
            vol_status = "⚪ Datar (Sideways)"

        # Tambahkan di bagian perhitungan indikator
        # Menghitung Volatilitas (Standard Deviation 20 periode)
        df['StdDev'] = df['Close'].rolling(window=20).std()
        # Menghitung Z-Score sederhana untuk evaluasi harga (apakah ekstrem atau tidak)
        df['Z-Score'] = (df['Close'] - df['Close'].rolling(window=20).mean()) / df['StdDev']

        # Ambil nilai terakhir
        last_std = float(df['StdDev'].iloc[-1]) if not pd.isna(df['StdDev'].iloc[-1]) else 0
        last_zscore = float(df['Z-Score'].iloc[-1]) if not pd.isna(df['Z-Score'].iloc[-1]) else 0

        # Evaluasi Risiko
        if last_zscore > 2:
            evaluasi = "🔴 Over-extended (Risiko Koreksi)"
        elif last_zscore < -2:
            evaluasi = "🟢 Undervalued (Potensi Rebound)"
        else:
            evaluasi = "⚪ Normal"
        return {
            "Ticker": ticker_name,
            "Live Price": last_price,
            "Change %": round(change_pct, 2),
            "VWAP/MA Baseline": round(last_vwap, 0),
            "Stoch %K": round(last_k, 2),
            "Stoch %D": round(last_d, 2),
            "RSI (14)": round(last_rsi, 2),
            "Est. Arah": direction,
            "Inst Flow": inst_flow,
            "Proteksi Stop Loss": stop_loss_est,
            "Estimasi Take Profit": take_profit_est,   
            "Dana Masuk %": f"{dana_masuk_pct}%",
            "Dana Keluar %": f"{dana_keluar_pct}%",
            "Net Foreign AVG": round((net_foreign_avg * last_price) / 1_000_000_000, 2),
            "Net Foreign (B)": round((net_foreign_val * last_price) / 1_000_000_000, 2),
            "Est Foreign Buy (B)": round((est_foreign_buy * last_price) / 1_000_000_000, 2),
            "Est Foreign Sell (B)": round((est_foreign_sell * last_price) / 1_000_000_000, 2),
            "Turnover (B)": round(total_turnover_today / 1_000_000_000, 2),
            "Momentum": momentum,
            "Status Sinyal": status_sinyal,
            "Vol Status": vol_status,
            "Volume Now": last_vol,
            "Volatilitas (StdDev)": round(last_std, 2),
            "Evaluasi Risiko": evaluasi
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
    
st.write(f"⏰ Jam Sinkronisasi Terakhir: **{wib_now.strftime('%d-%m-%Y %H:%M:%S')} WIB** (Zona Waktu Terkunci Asia/Jakarta)")
if st.button("🔄 Paksa Ambil Data Baru (Clear Cache)"):
    st.cache_data.clear()
    
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
        default=["BOLA","FILM","NIRO","WAPO","CARE","CTTH","PANS","BPII","BUMI","BBCA","BBRI","BBNI","BMRI","TLKM","BDMN","IMJS","IRSX","DSSA"])

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

        def style_scalper(row):
            styles = [''] * len(row)
            # ... (kode sebelumnya)
            
            # Tambahan styling untuk Inst Flow
            idx_flow = row.index.get_loc('Inst Flow')
            flow = str(row['Inst Flow'])
            if "Big Accum" in flow:
                styles[idx_flow] = 'background-color: #065F46; color: white;'
            elif "Big Dist" in flow:
                styles[idx_flow] = 'background-color: #991B1B; color: white;'
            return styles

            # Tambahan styling untuk Evaluasi Risiko
            idx_eval = row.index.get_loc('Evaluasi Risiko')
            eval_val = str(row['Evaluasi Risiko'])
            if "Over-extended" in eval_val:
                styles[idx_eval] = 'background-color: #7f1d1d; color: white;'
            elif "Undervalued" in eval_val:
                styles[idx_eval] = 'background-color: #064e3b; color: white;'
            return styles
    
        if not df_scalp.empty:
            styled_df = df_scalp.style.apply(style_scalper, axis=1)\
                                      .format({
                                          "Inst Flow": "{}",
                                          "Live Price": "Rp {:,.0f}",
                                          "Change %": "{:+.2f}%",                          
                                          "VWAP/MA Baseline": "Rp {:,.0f}",
                                          "Stoch %K": "{:.2f}",
                                          "Stoch %D": "{:.2f}",
                                          "RSI (14)": "{:.2f}",
                                          "Proteksi Stop Loss": "Rp {:,.0f}",
                                          "Estimasi Take Profit": "Rp {:,.0f}",
                                          "Dana Masuk %": "{}",
                                          "Dana Keluar %": "{}",
                                          "Net Foreign AVG": "{:,.2f} B",
                                          "Net Foreign (B)": "{:,.2f} B",                          
                                          "Est Foreign Buy (B)": "{:,.2f} B",
                                          "Est Foreign Sell (B)": "{:,.2f} B",
                                          "Turnover (B)": "{:,.2f} B",
                                          "Volatilitas (StdDev)": "{:.2f}",
                                          "Evaluasi Risiko": "{}"
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
