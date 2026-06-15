import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import pytz  
import concurrent.futures

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Swing & Scalper Dashboard BEI", layout="wide", page_icon="📈")

# Mengunci jam server ke zona waktu WIB (Asia/Jakarta)
wib_tz = pytz.timezone('Asia/Jakarta')
wib_now = datetime.now(wib_tz)

# --- 2. CUSTOM CSS UTK TAMPILAN PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #F8FAFC; }
    .main-title { color: #38BDF8; font-weight: 800; padding-bottom: 5px; }
    .sub-text { color: #94A3B8; font-size: 14px; margin-bottom: 20px; }
    .card-dana { background-color: #1E293B; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .card-ihsg { background-color: #1E293B; padding: 20px; border-radius: 12px; border-left: 5px solid #38BDF8; margin-bottom: 25px; }
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
        "WSBP", "WSKT", "WTG",  "WTIA", "YPAS", "YUASA", "YULE", "ZATA", "ZBRA", "ZINC", "ZONE", "PTRO", "BRAM", "IRSX", "WIFI", "KLBV","NCKL","BELI","ULTJ","TMPO", "DSSA","MDKA","RMKO","RMKE"
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

# --- 4. ENGINE ANALISIS UTAMA ---
def analyze_market_momentum(ticker):
    try:
        formatted_ticker = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
        
        # Mengembalikan konfigurasi ke mode harian 3 bulan standar yang stabil
        df = yf.download(formatted_ticker, period="3mo", interval="1d", progress=False)
        df = clean_yf_dataframe(df)
        
        if df is None or len(df) < 4 or 'Close' not in df.columns: 
            return None
        
        df['EMA9'] = ta.ema(df['Close'], length=9)
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        
        stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
        df['STOCHk'] = stoch['STOCHk_14_3_3'] if 'STOCHk_14_3_3' in stoch.columns else 50.0
        df['STOCHd'] = stoch['STOCHd_14_3_3'] if 'STOCHd_14_3_3' in stoch.columns else 50.0
        
        last_price = float(df['Close'].iloc[-1])
        last_ema9 = float(df['EMA9'].iloc[-1]) if not pd.isna(df['EMA9'].iloc[-1]) else last_price
        last_ema20 = float(df['EMA20'].iloc[-1]) if not pd.isna(df['EMA20'].iloc[-1]) else last_price
        last_ma50 = float(df['MA50'].iloc[-1]) if not pd.isna(df['MA50'].iloc[-1]) else last_price
        last_rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50.0
        last_k = float(df['STOCHk'].iloc[-1]) if not pd.isna(df['STOCHk'].iloc[-1]) else 50.0
        last_d = float(df['STOCHd'].iloc[-1]) if not pd.isna(df['STOCHd'].iloc[-1]) else 50.0
        last_volume = float(df['Volume'].iloc[-1])
        last_vol_ma = float(df['Vol_MA20'].iloc[-1]) if not pd.isna(df['Vol_MA20'].iloc[-1]) else 1.0
        
        prev_price = float(df['Close'].iloc[-2])
        change_pct = ((last_price - prev_price) / prev_price) * 100
        
        if change_pct >= 0:
            p_masuk = 50 + (min(change_pct * 5, 45))
        else:
            p_masuk = max(5, 50 - (abs(change_pct) * 5))
        
        p_masuk = max(5.0, min(95.0, p_masuk))
        p_keluar = 100.0 - p_masuk
        
        simulated_net_foreign = (last_volume * last_price * 0.12) / 1_000_000_000
        if change_pct < -1.0:
            simulated_net_foreign = -abs(simulated_net_foreign)
            
        if simulated_net_foreign > 15.0 and change_pct > 1.0:
            inst_flow = "🐋 Big Accum"
        elif simulated_net_foreign > 0 and change_pct > 0:
            inst_flow = "🐟 Small Accum"
        elif simulated_net_foreign < -15.0 and change_pct < -1.0:
            inst_flow = "🚨 Distribution"
        else:
            inst_flow = "⏳ Neutral"
            
        if last_volume > (last_vol_ma * 3.0):
            ids_disclosure = "⚠️ Unusual Vol"
        elif abs(change_pct) > 12.0:
            ids_disclosure = "📢 Corp Action"
        else:
            ids_disclosure = "✅ Normal"
            
        is_nego_active = "Yes" if last_volume > (last_vol_ma * 2.5) and abs(change_pct) < 0.2 else "No"
        simulated_nego_price = round(last_price * 0.98) if is_nego_active == "Yes" else last_price
        
        if last_price > last_ema20 and last_ema20 > last_ma50:
            trend_label = "🟩 Up-Trend"
        elif last_price < last_ema20 and last_ema20 < last_ma50:
            trend_label = "🟥 Down-Trend"
        else:
            trend_label = "🟨 Sideways"
            
        ticker_name = ticker.replace(".JK", "")
        
        if last_price > last_ema9 and last_k > last_d and last_rsi < 45 and last_volume > (last_vol_ma * 1.1):
            action_signal = "🔥 SUPER BUY"
            stop_loss = round(min(last_ema9, last_ema20), 0)
            take_profit = round(last_price + ((last_price - stop_loss) * 1.5), 0)
        elif last_k > last_d and (last_rsi < 35 or last_k < 25):
            action_signal = "🎯 BUY (Oversold)"
            stop_loss = round(last_price * 0.95, 0)
            take_profit = round(last_price * 1.05, 0)
        elif last_price < last_ema9 and last_k < last_d and last_rsi > 70:
            action_signal = "🚨 RISK (Jenuh Beli)"
            stop_loss = 0
            take_profit = 0
        else:
            action_signal = "⏳ Wait / Neutral"
            stop_loss = 0
            take_profit = 0
            
        return {
            "Ticker": ticker_name,
            "Price": last_price,
            "Change %": round(change_pct, 2),
            "Net For (B)": round(simulated_net_foreign, 2),
            "Inst Flow": inst_flow,
            "IDS Disclosure": ids_disclosure,
            "Dana Masuk %": round(p_masuk, 1),
            "Dana Keluar %": round(p_keluar, 1),
            "IDS Nego": is_nego_active,
            "Nego Price": simulated_nego_price,
            "RSI": round(last_rsi, 2),
            "Trend": trend_label,
            "Actionable": action_signal,
            "Proteksi SL": stop_loss,
            "Target TP": take_profit
        }
    except:
        return None

def run_mega_scanner(ticker_list):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        future_to_ticker = {executor.submit(analyze_market_momentum, t): t for t in ticker_list}
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            if res is not None:
                results.append(res)
    return pd.DataFrame(results)

# --- 5. INTERFACE PANEL UTAMA ---
st.markdown("<h1 class='main-title'>📈 Swing Trading & Scalper Radar Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>Sistem pemindaian otomatis berskala 300+ Emiten Bursa Efek Indonesia</p>", unsafe_allow_html=True)

# ----------------- TRACKER MULTI-TIMEFRAME CHART IHSG -----------------
st.markdown("<div class='card-ihsg'>", unsafe_allow_html=True)

tf_col1, tf_col2 = st.columns(2)
with tf_col2:
    timeframe_pilihan = st.radio(
        "Pilih Rentang Waktu Grafik:",
        options=["Hari (5 Hari)", "Minggu (1 Bulan)", "Bulan (6 Bulan)", "Tahun (1 Tahun)"],
        horizontal=True
    )

tf_mapping = {
    "Hari (5 Hari)": {"period": "5d", "interval": "15m", "label": "Batas (5 Hari)"},
    "Minggu (1 Bulan)": {"period": "1mo", "interval": "1d", "label": "Batas (1 Bulan)"},
    "Bulan (6 Bulan)": {"period": "6mo", "interval": "1d", "label": "Batas (6 Bulan)"},
    "Tahun (1 Tahun)": {"period": "1y", "interval": "1d", "label": "Batas (1 Tahun)"}
}

p_conf = tf_mapping[timeframe_pilihan]

try:
    ihsg_data = yf.download("^JKSE", period=p_conf["period"], interval=p_conf["interval"], progress=False)
    ihsg_data = clean_yf_dataframe(ihsg_data)
    
    ihsg_live = yf.download("^JKSE", period="7d", interval="1d", progress=False)
    ihsg_live = clean_yf_dataframe(ihsg_live)
    
    if ihsg_data is not None and not ihsg_data.empty:
        current_ihsg = float(ihsg_live['Close'].iloc[-1])
        prev_ihsg = float(ihsg_live['Close'].iloc[-2])
        ihsg_change = ((current_ihsg - prev_ihsg) / prev_ihsg) * 100
        
        ihsg_high = float(ihsg_data['High'].max())
        ihsg_low = float(ihsg_data['Low'].min())
        
        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        with col_i1:
            st.metric(label="📌 IHSG Update Saat Ini", value=f"{current_ihsg:,.2f}", delta=f"{ihsg_change:+.2f}%")
        with col_i2:
            st.metric(label=f"📈 {p_conf['label']} Max", value=f"{ihsg_high:,.2f}")
        with col_i3:
            st.metric(label=f"📉 {p_conf['label']} Min", value=f"{ihsg_low:,.2f}")
        with col_i4:
            status_pasar = "🚨 Gawat / Bearish" if ihsg_change < -1.2 else "⏳ Konsolidasi" if abs(ihsg_change) <= 1.2 else "🚀 Bullish Kuat"
            st.metric(label="⚡ Kondisi Sentimen Harian", value=status_pasar)
        
        st.markdown(f"**📊 Grafik Pergerakan Histori IHSG Rentang: {timeframe_pilihan}**")
        chart_df = ihsg_data[['Close']].copy()
        st.line_chart(chart_df, height=220)
        
except Exception as e:
    st.warning("⚠️ Gagal memuat chart IHSG, silakan klik refresh.")

st.markdown("</div>", unsafe_allow_html=True)

# Keterangan diperbarui tanpa embel-embel auto-refresh
st.write(f"⏰ Jam Sinkronisasi Terakhir: **{wib_now.strftime('%d-%m-%Y %H:%M:%S')} WIB** (Delay Yahoo Finance ±10-15 Menit)")

if st.button("🔄 Paksa Ambil Data Baru (Clear Cache)"):
    st.cache_data.clear()

# PANEL SIDEBAR
with st.sidebar:
    st.header("⚙️ Panel Filter Pencarian")
    filter_mode = st.radio(
        "Saring Kategori Sinyal:",
        options=["Tampilkan Semua Emiten", "Hanya Sinyal BUY / SUPER BUY", "Hanya Struktur Up-Trend"]
    )
    st.markdown("---")
    saham_pilihan = st.multiselect(
        "Kustom Pilih / Ketik Kode Saham Tambahan:",
        options=master_tickers_clean,
        default=["AADI", "BBCA", "BBRI", "BBNI", "BBTN", "INDF", "ICBP", "CBDK", "CMRY", "AMRT", "ANTM", "KLBF", "KAEF", "INKP", "ITMG", "UNTR", "GGRM", "SGRO","HRTA","BRMS","BUVA","CPIN","ADRO","BUMI","PTRO","ENRG","JPFA","FILM","MYOR","NCKL","BELI","ULTJ","DSSA","IRSX", "WIFI","MDKA","RMKO","RMKE", "KLBV", "TMPO"])

# RENDERING TABEL UTAMA & METRIK PERSENTASE DANA
if len(saham_pilihan) > 0:
    with st.spinner("Sedang memproses bandarmologi dan data bursa..."):
        df_radar = run_mega_scanner(saham_pilihan)
    
    if not df_radar.empty:
        avg_masuk = float(df_radar["Dana Masuk %"].mean())
        avg_keluar = 100.0 - avg_masuk
        
        st.markdown(f"""
        <div class='card-dana'>
            <div style='display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 5px;'>
                <span style='color: #4ADE80;'>🟢 Rata-rata Dana Masuk: {avg_masuk:.1f}%</span>
                <span style='color: #F87171;'>🔴 Rata-rata Dana Keluar: {avg_keluar:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(avg_masuk / 100.0)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if filter_mode == "Hanya Sinyal BUY / SUPER BUY":
            df_radar = df_radar[df_radar["Actionable"].str.contains("BUY")]
        elif filter_mode == "Hanya Struktur Up-Trend":
            df_radar = df_radar[df_radar["Trend"].str.contains("Up-Trend")]
            
        df_radar = df_radar.sort_values(by="Change %", ascending=False)
        
        def style_radar_rows(row):
            styles = [''] * len(row)
            action = str(row['Actionable'])
            trend = str(row['Trend'])
            flow = str(row['Inst Flow'])
            disc = str(row['IDS Disclosure'])
            
            idx_action = row.index.get_loc('Actionable')
            idx_trend = row.index.get_loc('Trend')
            idx_flow = row.index.get_loc('Inst Flow')
            idx_disc = row.index.get_loc('IDS Disclosure')
            idx_masuk = row.index.get_loc('Dana Masuk %')
            idx_keluar = row.index.get_loc('Dana Keluar %')
            
            styles[idx_masuk] = 'color: #4ADE80; font-weight: bold;'
            styles[idx_keluar] = 'color: #F87171;'
            
            if "SUPER BUY" in action:
                styles[idx_action] = 'background-color: #15803D; color: white; font-weight: bold;'
            elif "BUY" in action:
                styles[idx_action] = 'background-color: #166534; color: #BBF7D0;'
                
            if "Up-Trend" in trend or "Accum" in flow:
                if "Up-Trend" in trend: styles[idx_trend] = 'color: #4ADE80;'
                if "Accum" in flow: styles[idx_flow] = 'color: #4ADE80; font-weight: bold;'
            elif "Down-Trend" in trend or "Distribution" in flow:
                if "Down-Trend" in trend: styles[idx_trend] = 'color: #F87171;'
                if "Distribution" in flow: styles[idx_flow] = 'color: #F87171; font-weight: bold;'
                
            if "Unusual" in disc or "Action" in disc:
                styles[idx_disc] = 'color: #FBBF24; font-weight: bold;'
                
            return styles

        if not df_radar.empty:
            styled_df = df_radar.style.apply(style_radar_rows, axis=1)\
                                      .format({
                                          "Price": "Rp {:,.0f}",
                                          "Change %": "{:+.2f}%",
                                          "Net For (B)": "{:+.2f} B",
                                          "Dana Masuk %": "{:.1f}%",
                                          "Dana Keluar %": "{:.1f}%",
                                          "Nego Price": "Rp {:,.0f}",
                                          "RSI": "{:.2f}",
                                          "Proteksi SL": "Rp {:,.0f}",
                                          "Target TP": "Rp {:,.0f}"
                                      })
            
            st.dataframe(styled_df, use_container_width=True, height=520)
        else:
            st.warning("⚠️ Tidak ada emiten dari daftar Anda yang lolos kriteria filter saat ini.")
else:
    st.info("👋 Silakan pilih atau tambahkan minimal 1 kode emiten pada kolom sidebar untuk memulai radar.")
