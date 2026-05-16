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

# --- 3. DATABASE EMITEN BEI ---
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
        elif last_price > last_ma20:
            keterangan = "Diatas MA20"
        elif last_price > last_ma50:
            keterangan = "Diatas MA50"
        else:
            keterangan = "Dibawah MA Harian"
            
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
            "Volume": last_volume,
            "MA20": round(last_ma20, 1),
            "MA50": round(last_ma50, 1),
            "RSI": round(last_rsi, 2),
            "Trend": trend,
            "Keterangan": keterangan,
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
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
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
        saham_di_scan = st.multiselect("Ketik & Pilih Kode Saham:", options=master_tickers_clean, default=["BBCA", "BBRI", "AADI", "CMRY"])
    else:
        abjad = st.radio("Pilih Huruf Depan:", ["A-D", "E-J", "K-P", "Q-T", "U-Z"])
        ranges = abjad.split("-")
        saham_di_scan = [t for t in master_tickers_clean if len(t) > 0 and ranges <= t <= ranges]

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
            kolom_rapi = ["Ticker", "Price", "Change %", "Volume", "MA20", "MA50", "RSI", "Trend", "Keterangan", "Actionable"]
            
            for col in kolom_rapi:
                if col not in df_scan.columns:
                    df_scan[col] = 0.0 if col in ["Price", "Change %", "Volume", "MA20", "MA50", "RSI"] else "-"
                    
            df_display = df_scan[kolom_rapi].copy()

            def color_scanner_rows(row):
                styles = [''] * len(row)
                act_val = str(row['Actionable'])
                trend_val = str(row['Trend'])
                ket_val = str(row['Keterangan'])
                
                idx_act = row.index.get_loc('Actionable')
                idx_trend = row.index.get_loc('Trend')
                idx_ket = row.index.get_loc('Keterangan')
                
                if "BUY" in act_val:
                    styles[idx_act] = 'background-color: #d4edda; color: #155724; font-weight: bold;'
                elif "SELL" in act_val:
                    styles[idx_act] = 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
                
                if "Up-Trend" in trend_val:
                    styles[idx_trend] = 'color: #28a745; font-weight: bold;'
                elif "Down-Trend" in trend_val:
                    styles[idx_trend] = 'color: #dc3545; font-weight: bold;'
                    
                if "Strong" in ket_val:
                    styles[idx_ket] = 'color: #0056b3; font-weight: bold;'
                    
                return styles

            styled_df = df_display.style.apply(color_scanner_rows, axis=1)\
                                     .format({
                                         "Price": "Rp {:,.0f}", 
                                         "Change %": "{:+.2f}%", 
                                         "Volume": "{:,.0f}",
                                         "MA20": "Rp {:,.1f}",
                                         "MA50": "Rp {:,.1f}",
                                         "RSI": "{:.2f}"
                                     })
            
            st.dataframe(styled_df, use_container_width=True, height=550)
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
        fig_bar.update_layout(
            title="Perubahan Harga Saham (%) Hari Ini (Maks. 40 Emiten)", 
            yaxis_title="Persentase Perubahan", 
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Data visualisasi belum tersedia. Jalankan scanner di Tab 1 terlebih dahulu.")

# --- TAB 3: INTERACTIVE ANALYSIS ---
with tab3:
    st.subheader(f"Analisis Teknikal Mendalam: {selected_stock}")
    
    ticker_jk = f"{selected_stock}.JK"
    df_stock = get_single_stock_data(ticker_jk)
    
    if df_stock is not None and not df_stock.empty and len(df_stock) >= 2 and 'Close' in df_stock.columns and 'Open' in df_stock.columns:
        try:
            c_price = float(df_stock['Close'].iloc[-1])
            p_price = float(df_stock['Close'].iloc[-2])
            
            diff = c_price - p_price
            pct = (diff / p_price) * 100 if p_price != 0 else 0.0
            
            val_rsi = float(df_stock['RSI'].iloc[-1]) if not pd.isna(df_stock['RSI'].iloc[-1]) else 50.0
            val_ma50 = float(df_stock['MA50'].iloc[-1]) if not pd.isna(df_stock['MA50'].iloc[-1]) else c_price
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Harga Terakhir", value=f"Rp {c_price:,.0f}", delta=f"{diff:+.0f} ({pct:+.2f}%)")
            with col2:
                status_rsi = "Oversold (<35)" if val_rsi < 35 else ("Overbought (>70)" if val_rsi > 70 else "Neutral")
                st.metric(label="RSI (14)", value=f"{val_rsi:.2f}", delta=status_rsi)
            with col3:
                status_ma = "Di atas MA50 (Bullish)" if c_price > val_ma50 else "Di bawah MA50 (Bearish)"
                st.metric(label="Posisi MA50", value=f"Rp {val_ma50:,.0f}", delta=status_ma)
            
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
            
            # --- TABEL ESTIMASI KENAIKAN & PENURUNAN (SCALPING) ---
            st.markdown("---")
            st.subheader(f"⚡ Kalkulator & Estimasi Target Scalping: {selected_stock}")
            
            try:
                raw_atr = df_stock['ATR'].dropna().iloc[-1] if 'ATR' in df_stock.columns else None
                atr_val = float(raw_atr) if (raw_atr is not None and not pd.isna(raw_atr) and raw_atr > 0) else float(c_price * 0.025)
            except:
                atr_val = float(c_price * 0.025)
            
            tp1_scalping = c_price + (atr_val * 0.5)
            tp2_scalping = c_price + (atr_val * 1.0)
            sl_scalping = c_price - (atr_val * 0.5)
            
            pct_tp1 = ((tp1_scalping - c_price) / c_price) * 100
            pct_tp2 = ((tp2_scalping - c_price) / c_price) * 100
            pct_sl = ((sl_scalping - c_price) / c_price) * 100
            
            def sesuaikan_fraksi_bei(harga):
                if harga < 200: return round(harga)
                elif harga < 500: return round(harga / 2) * 2
                elif harga < 2000: return round(harga / 5) * 5
                elif harga < 5000: return round(harga / 10) * 10
                else: return round(harga / 25) * 25
                
            tp1_clean = sesuaikan_fraksi_bei(tp1_scalping)
            tp2_clean = sesuaikan_fraksi_bei(tp2_scalping)
            sl_clean = sesuaikan_fraksi_bei(sl_scalping)
            
            data_scalping = {
                "Skenario Pergerakan": [
                    "🚀 Take Profit 1 (Target Konservatif)", 
                    "🔥 Take Profit 2 (Target Maksimal Harian)", 
                    "🛑 Stop Loss (Batas Risiko Maksimal)"
                ],
                "Estimasi Harga Target": [tp1_clean, tp2_clean, sl_clean],
                "Estimasi Persentase (+/-)": [f"+{pct_tp1:.2f}%", f"+{pct_tp2:.2f}%", f"{pct_sl:.2f}%"],
                "Rekomendasi Aksi": [
                    "Jual Parsial / Amankan Profit Terdekat", 
                    "Jual Bersih / Amankan Seluruh Keuntungan", 
                    "Disiplin Cut Loss Jika Level Ini Tertembus"
                ]
            }
            
            df_scalping_table = pd.DataFrame(data_scalping)
            
            def color_scalping_rows(row):
                styles = [''] * len(row)
                if "Take Profit" in row["Skenario Pergerakan"]:
                    styles = 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
                    styles = 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
                elif "Stop Loss" in row["Skenario Pergerakan"]:
                    styles = 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
                    styles = 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
                return styles

            styled_scalping = df_scalping_table.style.apply(color_scalping_rows, axis=1)\
                                                    .format({"Estimasi Harga Target": "Rp {:,.0f}"})
            
            st.dataframe(styled_scalping, use_container_width=True, hide_index=True)
            st.caption(f"*Metode perhitungan di atas didasarkan pada nilai **ATR (14 Harian) sebesar Rp {atr_val:.1f}**. Target harga disesuaikan secara otomatis dengan struktur fraksi harga (tick size) Bursa Efek Indonesia.")

        except Exception as e:
            st.error(f"Terjadi kesalahan teknis saat merender grafik & tabel: {str(e)}")
    else:
        st.warning(f"⚠️ Yahoo Finance tidak mengembalikan data untuk saham {selected_stock} saat ini. Silakan coba pilih kode saham lain pada menu Sidebar.")

# --- 11. FOOTER ---
st.markdown("---")
st.markdown(f"© {datetime.now().year} **SwingScanner Pro** | Menggunakan Streamlit Modern | Data Source: Yahoo Finance")
