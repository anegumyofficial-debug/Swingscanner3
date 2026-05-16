import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
import concurrent.futures

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

# --- 3. DATABASE EMITEN BEI RAKSASA (SUDAH TERMASUK AADI, CMRY, MORA, ELPI, DSSA, DLL) ---
@st.cache_data(ttl=604800)
def load_all_indonesia_tickers():
    saham_bei = [
        # --- PERBANKAN & KEUANGAN ---
        "BBCA", "BBRI", "BMRI", "BBNI", "BRIS", "BBTN", "BDMN", "BTPN", "BJBR", "BJTM", 
        "AGRO", "BCIC", "BINA", "DNAR", "MAYB", "MEGA", "PNBN", "PNBS", "BVIC", "BBHI", 
        "ARTO", "BBYB", "BYBK", "BNGA", "BNLI", "BSIM", "NISP", "PNLF", "PANS", "ADMF",
        "BCAP", "BBLD", "BABP", "BACA", "BESS", "CFIN", "DEFI", "GSMF", "MASB", "NOBU",
        
        # --- TAMBANG, ENERGI, MINERAL & SAHAM KELOMPOK DIAN SWASTATIKA ---
        "AADI", "ADRO", "PTBA", "ITMG", "HRUM", "INDY", "DOID", "KKGI", "BYAN", "GEMS", 
        "BUMI", "DEWA", "TOBA", "MEDC", "ENRG", "PGAS", "AKRA", "PGEO", "ANTM", "TINS", 
        "INCO", "MDKA", "MBMA", "NCKL", "BRMS", "DKFT", "PSAB", "ZINC", "IFSH", "MBAP", 
        "SGER", "DSSA", "ELPI", "APEX", "ARTI", "BIPI", "BOSS", "BESS", "CTTH", "CUAN",
        "D限制", "GREN", "IATA", "MDVS", "MITI", "PKPK", "RMKO", "RMKE", "SURE", "WOWS",
        
        # --- INFRASTRUKTUR, TELEKOMUNIKASI, LOGISTIK & MENARA ---
        "MORA", "TLKM", "EXCL", "ISAT", "FREN", "TOWR", "TBIG", "CENT", "JSMR", "BIRD", 
        "SMDR", "TMAS", "ASSA", "META", "CMNP", "POWR", "KEEN", "ARKO", "WEGE", "WIKA", 
        "PTPP", "ADHI", "TOTL", "ACST", "BPII", "BLTA", "GIAA", "NELY", "HAIS", "IPCM",
        "BALI", "BUKK", "CASS", "GHON", "GIPH", "HITS", "IBST", "JAST", "LINK", "PORT",
        
        # --- BARANG KONSUMEN PRIMER (Makanan, Rokok, Susu & Kebun) ---
        "CMRY", "INDF", "ICBP", "UNVR", "MYOR", "GGRM", "HMSP", "WIIM", "AALI", "LSIP", 
        "SIMP", "BWPT", "TAPG", "DSNG", "SSMS", "CLEO", "CAMP", "ROTI", "GOOD", "PSSI", 
        "STAA", "TBLA", "SGRO", "SMAR", "CPRO", "JPFA", "CPIN", "MAIN", "WMUU", "AISA",
        "ALTO", "BISI", "BTEK", "BUDI", "CEKA", "DLTA", "FOOD", "IKAN", "KEJU", "PANI",
        
        # --- BARANG KONSUMEN NON-PRIMER (Ritel, Media, Otomotif, Mainan) ---
        "ASII", "ACES", "MAPI", "MAPA", "ERAA", "RALS", "AMRT", "MEDI", "MNCN", "SCMA", 
        "EMTK", "NETV", "AUTO", "DRMA", "SMSM", "GJTL", "MASA", "IMAS", "LPPF", "CBDK",
        "PMMP", "PANR", "BUVA", "MDIA", "FORU", "AGAR", "AMMS", "BABY", "BELI", "BIPN", 
        "CARS", "EPAC", "FILM", "GLOB", "HOME", "HOTL", "IKBI", "KBLA", "LPIN", "MSIN",
        
        # --- KESEHATAN & FARMASI ---
        "KLBF", "MIKA", "HEAL", "SILO", "SAME", "PRDA", "TSPC", "KAEF", "INAF", "PEHA", 
        "BMHS", "IRRA", "OMED", "SIDO", "ASTA", "CARE", "DGNS", "MREI", "PRIM", "SOCI",
        
        # --- PROPERTI & REAL ESTATE ---
        "BSDE", "PWON", "CTRA", "SMRA", "ASRI", "DUTI", "DILD", "PPRO", "LPCK", "LPKR", 
        "MDLN", "BKSL", "KIJA", "BEST", "SSIA", "AMAN", "BAPA", "FMII", "GAMA", "JRPT",
        "ADMG", "AMOR", "APLN", "BIPP", "COCO", "CPRI", "DMAS", "EMDE", "GAMA", "GURA",
        
        # --- TEKNOLOGI & DIGITAL EKONOMI ---
        "GOTO", "BUKA", "WIFI", "ATIC", "HDIT", "MLPT", "MCAS", "DIVA", "ASPI", "GLVA", 
        "ZYRX", "AWAN", "BTEL", "CHIP", "CYBR", "DNAR", "KREN", "LUCK", "PTMP", "SKYB",
        
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
        change_pct = ((last_price - prev_price) / prev_price) * 100
        
        last_rsi = float(df['RSI'].iloc[-1])
        last_ma20 = float(df['MA20'].iloc[-1])
        last_ma50 = float(df['MA50'].iloc[-1])
        prev_ma20_val = float(df['MA20'].iloc[-2])
        
        trend = "Up-Trend" if last_price > last_ma50 else "Down-Trend"
        
        if last_rsi < 35:
            action = "BUY (Oversold)"
        elif last_price > last_ma20 and prev_price <= prev_ma20_val:
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

# --- 6. CORE BULK SCANNER ---
@st.cache_data(ttl=600) 
def run_bulk_scanner(ticker_list):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_ticker = {executor.submit(fetch_and_analyze_stock, t): t for t in ticker_list}
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            if res is not None:
                results.append(res)
    return pd.DataFrame(results)

# --- 7. SINGLE STOCK FETCH ---
@st.cache_data(ttl=120)
def get_single_stock_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        df = clean_yf_dataframe(df)
        if df is None or len(df) < 20 or 'Close' not in df.columns:
            return None
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        return df
    except:
        return None

# --- 8. TAMPILAN UTAMA ---
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
        saham_di_scan = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "GOTO", "UNVR", "ADRO", "PTBA", "BRIS", "ANTM", "INDF", "ICBP", "KLBF", "AMMN", "MDKA", "SIDO", "AADI", "CMRY"]
    elif pilihan_mode == "Kustom Pilih Sendiri (Multi-Select)":
        saham_di_scan = st.multiselect("Ketik & Pilih Kode Saham:", options=master_tickers_clean, default=["BBCA", "BBRI", "AADI", "CMRY", "DSSA"])
    else:
        abjad = st.radio("Pilih Huruf Depan:", ["A-D", "E-J", "K-P", "Q-T", "U-Z"])
        saham_di_scan = [t for t in master_tickers_clean if t in abjad.replace("-", "")]

    st.markdown("---")
    st.subheader("🔍 Grafik Detail")
    selected_stock = st.selectbox("Pilih Saham untuk Grafik Detail (Tab 3):", options=master_tickers_clean, index=0)
    
    st.markdown("---")
    st.info(f"📁 Total Database BEI Aktif: {len(master_tickers_clean)} Emiten.")

# --- 10. TABS LAYOUT ---
tab1, tab2, tab3 = st.tabs(["🔍 Actionable Scanner", "🔥 Market Heatmap", "📊 Interactive Analysis"])

# --- TAB 1: SCANNER ---
df_scan = pd.DataFrame()  
with tab1:
    st.subheader("Hasil Pemindaian Pasar Harian")
    
    if len(saham_di_scan) == 0:
        st.warning("Silakan pilih emiten terlebih dahulu pada menu Sidebar.")
    else:
        with st.spinner(f"Memindai data teknikal {len(saham_di_scan)} emiten secara paralel..."):
            df_scan = run_bulk_scanner(saham_di_scan)

        if df_scan is not None and not df_scan.empty:
            def color_rows(val):
                val_str = str(val)
                if "BUY" in val_str: return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                if "SELL" in val_str: return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
                if "Up-Trend" in val_str: return 'color: #28a745; font-weight: bold;'
                if "Down-Trend" in val_str: return 'color: #dc3545; font-weight: bold;'
                return ''

            styled_df = df_scan.style.map(color_rows, subset=['Actionable', 'Trend'])\
                                     .format({"Price": "Rp {:,.0f}", "Change %": "{:+.2f}%", "RSI": "{:.2f}"})
            
            st.dataframe(styled_df, use_container_width=True, height=500)
        else:
            st.error("Gagal mendapatkan data scanner. Coba pilih kelompok emiten yang berbeda.")

# --- TAB 2: MARKET OVERVIEW ---
with tab2:
    st.subheader("Market Performance Overview")
    if df_scan is not None and not df_scan.empty:
        df_chart = df_scan.sort_values(by="Change %", ascending=False).head(40)
        fig_bar = go.Figure(go.Bar(
            x=df_chart['Ticker'],
            y=df_chart['Change %'],
            marker_color=['#28a745' if change > 0 else '#dc3545' for change in df_chart['Change %']]
        ))
        fig_bar.update_layout(title="Perubahan Harga Saham (%) Hari Ini (Maks. 40 Emiten)", yaxis_title="Persentase Perubahan", template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Data visualisasi belum tersedia. Jalankan scanner di Tab 1 terlebih dahulu.")

# --- TAB 3: INTERACTIVE ANALYSIS ---
with tab3:
    st.subheader(f"Analisis Teknikal Mendalam: {selected_stock}")
    
    ticker_jk = f"{selected_stock}.JK"
    df_stock = get_single_stock_data(ticker_jk)
    
    if df_stock is not None and not df_stock.empty and len(df_stock) >= 2 and 'Close' in df_stock.columns:
        try:
            c_price = float(df_stock['Close'].iloc[-1])
            p_price = float(df_stock['Close'].iloc[-2])
            
            diff = c_price - p_price
            pct = (diff / p_price) * 100
            rsi_val = float(df_stock['RSI'].iloc[-1])
            ma50_val = float(df_stock['MA50'].iloc[-1])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Harga Terakhir", value=f"Rp {c_price:,.0f}", delta=f"{diff:+.0f} ({pct:+.2f}%)")
            with col2:
                delta_rsi = "Oversold (<35)" if rsi_val < 35 else ("Overbought (>70)" if rsi_val > 70 else "Neutral")
                st.metric(label="RSI (14)", value=f"{rsi_val:.2f}", delta=delta_rsi)
            with col3:
                delta_ma = "Di atas MA50 (Bullish)" if c_price > ma50_val else "Di bawah MA50 (Bearish)"
                st.metric(label="Posisi MA50", value=f"Rp {ma50_val:,.0f}", delta=delta_ma)
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df_stock.index,
                open=df_stock['Open'].squeeze(), 
                high=df_stock['High'].squeeze(),
                low=df_stock['Low'].squeeze(), 
                close=df_stock['Close'].squeeze(),
                name="Harga Saham"
            ))
            
            fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['MA20'].squeeze(), line=dict(color='orange', width=1.5), name="MA 20"))
            fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['MA50'].squeeze(), line=dict(color='blue', width=1.5), name="MA 50"))
            
            fig.update_layout(
                title=f"Grafik Historis {selected_stock} (1 Tahun Terakhir)",
                xaxis_title="Tanggal", yaxis_title="Harga (IDR)",
                xaxis_rangeslider_visible=False, template="plotly_white",
                height=500, hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Terjadi kesalahan teknis saat merender grafik: {str(e)}")
    else:
        st.warning(f"⚠️ Yahoo Finance tidak mengembalikan data untuk {selected_stock}. Silakan coba pilih kode saham lain.")

# --- 11. FOOTER ---
st.markdown("---")
st.markdown(f"© {datetime.now().year} **SwingScanner Pro** | Menggunakan Streamlit Modern | Data Source: Yahoo Finance")
