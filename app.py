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

# --- 3. OTOMATIS AMBIL SELURUH DAFTAR EMITEN INDONESIA ---
@st.cache_data(ttl=86400) # Simpan daftar emiten selama 24 jam di cache
def load_all_indonesia_tickers():
    try:
        # Menarik data komprehensif seluruh emiten dari open-source data IDX publik
        url = "https://raw.githubusercontent.com/hellonoor/saham-indonesia/master/data/saham.csv"
        df_all = pd.read_csv(url)
        
        if 'code' in df_all.columns:
            raw_list = df_all['code'].tolist()
        elif 'Ticker' in df_all.columns:
            raw_list = df_all['Ticker'].tolist()
        else:
            raw_list = []
        
        cleaned_list = []
        for code in raw_list:
            c_clean = str(code).strip().upper()
            if not c_clean.endswith(".JK"):
                c_clean = f"{c_clean}.JK"
            if len(c_clean) <= 8:  # Memastikan format data ticker valid
                cleaned_list.append(c_clean)
        
        return sorted(list(set(cleaned_list)))
    except:
        # Fallback cadangan jika tautan eksternal terputus
        return [f"{s}.JK" for s in ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "GOTO", "UNVR", "ADRO", "PTBA", "BRIS", "ANTM", "KLBF", "INDF"]]

# Inisialisasi daftar emiten
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

# --- 5. SATUAN FUNGSI SCANNING PER SAHAM (UNTUK PARALEL) ---
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
@st.cache_data(ttl=900) # Cache hasil scan massal selama 15 menit
def run_bulk_scanner(ticker_list):
    results = []
    # Menggunakan max_workers=15 agar pemrosesan cepat namun tidak memicu rate-limit Yahoo Finance
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_ticker = {executor.submit(fetch_and_analyze_stock, t): t for t in ticker_list}
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            if res is not None:
                results.append(res)
    return pd.DataFrame(results)

# --- 7. GRAPH FETCHING (SINGLE STOCK ANALYSIS) ---
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
        ["Saham Pilihan Utama (LQ45/Bluechip)", "Kustom Pilih Sendiri (Multi-Select)", "Scan Berdasarkan Sektor Utama"]
    )
    
    if pilihan_mode == "Saham Pilihan Utama (LQ45/Bluechip)":
        saham_di_scan = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "GOTO", "UNVR", "ADRO", "PTBA", "BRIS", "ANTM", "INDF", "ICBP", "KLBF", "AMMN", "CPIN", "MDKA"]
    elif pilihan_mode == "Kustom Pilih Sendiri (Multi-Select)":
        saham_di_scan = st.multiselect(
            "Ketik/Pilih Kode Saham BEI:", 
            options=master_tickers_clean, 
            default=["BBCA", "BBRI", "BMRI", "BBNI", "TLKM"]
        )
    else:
        # Memisahkan emiten per kelompok alphabet/sektor agar scanner tidak kelebihan beban jika ingin melihat list luas
        kelompok_abjad = st.selectbox("Pilih Urutan Abjad Emiten:", ["A - D", "E - J", "K - P", "Q - T", "U - Z"])
        if kelompok_abjad == "A - D":
            saham_di_scan = [t for t in master_tickers_clean if t in "ABCD"]
        elif kelompok_abjad == "E - J":
            saham_di_scan = [t for t in master_tickers_clean if t in "EFGHIJ"]
        elif kelompok_abjad == "K - P":
            saham_di_scan = [t for t in master_tickers_clean if t in "KLMNOP"]
        elif kelompok_abjad == "Q - T":
            saham_di_scan = [t for t in master_tickers_clean if t in "QRST"]
        else:
            saham_di_scan = [t for t in master_tickers_clean if t in "UVWXYZ"]

    st.markdown("---")
    st.subheader("🔍 Grafik Detail")
    selected_stock = st.selectbox(
        "Pilih Saham untuk Grafik Detail (Tab 3):", 
        master_tickers_clean, 
        index=master_tickers_clean.index("BBCA") if "BBCA" in master_tickers_clean else 0
    )
    
    st.markdown("---")
    st.info(f"📁 Total Database BEI Aktif: {len(master_tickers_clean)} Emiten.")

# --- 10. TABS LAYOUT ---
tab1, tab2, tab3 = st.tabs(["🔍 Actionable Scanner", "🔥 Market Heatmap", "📊 Interactive Analysis"])

# --- TAB 1: SCANNER ---
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
            st.error("Gagal mendapatkan data scanner. Coba pilih kelompok emiten yang lebih kecil.")

# --- TAB 2: MARKET OVERVIEW ---
with tab2:
    st.subheader("Market Performance Overview")
    if 'df_scan' in locals() and df_scan is not None and not df_scan.empty:
        # Batasi rendering heatmap maksimal 40 emiten teratas agar grafik tetap rapi dibaca
        df_chart = df_scan.head(40)
        fig_bar = go.Figure(go.Bar(
            x=df_chart['Ticker'],
            y=df_chart['Change %'],
            marker_color=['#28a745' if change > 0 else '#dc3545' for change in df_chart['Change %']]
        ))
        fig_bar.update_layout(title="Perubahan Harga Saham (%) Hari Ini (Maks. 40 Emiten)", yaxis_title="Persentase Perubahan", template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Data visualisasi belum tersedia. Saring kode saham terlebih dahulu di sidebar.")

# --- TAB 3: INTERACTIVE ANALYSIS ---
with tab3:
    st.subheader(f"Analisis Teknikal Mendalam: {selected_stock}")
    
    ticker_jk = f"{selected_stock}.JK"
    df_stock = get_single_stock_data(ticker_jk)
    
    if df_stock is not None and not df_stock.empty and len(df_stock) >= 2:
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
                open=df_stock['Open'], high=df_stock['High'],
                low=df_stock['Low'], close=df_stock['Close'],
                name="Harga Saham"
            ))
            
            fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['MA20'], line=dict(color='orange', width=1.5), name="MA 20"))
            fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['MA50'], line=dict(color='blue', width=1.5), name="MA 50"))
            
            fig.update_layout(
                title=f"Grafik Historis {selected_stock} (1 Tahun Terakhir)",
                xaxis_title="Tanggal", yaxis_title="Harga (IDR)",
                xaxis_rangeslider_visible=False, template="plotly_white",
                height=500, hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Terjadi kesalahan pemrosesan kolom data: {str(e)}")
    else:
        st.warning(f"⚠️ Yahoo Finance tidak mengembalikan data untuk {selected_stock}. Silakan coba pilih kode saham lain.")

# --- 11. FOOTER ---
st.markdown("---")
st.markdown(f"© {datetime.now().year} **SwingScanner Pro** | Menggunakan Streamlit Modern | Data Source: Yahoo Finance")
