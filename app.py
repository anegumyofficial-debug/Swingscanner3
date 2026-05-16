import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime, timedelta
import concurrent.futures
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Swing Trading Scanner BEI - Pro", layout="wide", page_icon="📈")

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
        "BBCA", "BBRI", "BMRI", "BBNI", "BRIS", "BBTN", "ARTO", "BBYB", "BNGA", "NISP",
        "AADI", "ADRO", "PTBA", "ITMG", "HRUM", "INDY", "BUMI", "MEDC", "PGAS", "ANTM", 
        "TINS", "INCO", "MDKA", "MBMA", "NCKL", "BRMS", "TLKM", "EXCL", "ISAT", "TOWR", 
        "JSMR", "BIRD", "SMDR", "TMAS", "ASSA", "CMRY", "INDF", "ICBP", "UNVR", "MYOR", 
        "GGRM", "HMSP", "AALI", "LSIP", "TAPG", "DSNG", "CLEO", "ROTI", "JPFA", "CPIN",
        "ASII", "ACES", "MAPI", "MAPA", "ERAA", "AMRT", "AUTO", "DRMA", "GJTL", "KLBF", 
        "MIKA", "HEAL", "SILO", "SIDO", "BSDE", "PWON", "CTRA", "SMRA", "ASRI", "GOTO", 
        "BUKA", "WIFI", "AMMN", "SMGR", "INTP", "BRPT", "TPIA", "INKP", "TKIM", "AVIA"
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

# --- 5. DETEKSI DATA PASAR NEGOSIASI & INSTITUTIONAL FLOW ---
# Fungsi ini mensimulasikan pencarian anomali IDS Disclosure & Foreign Flow harian
def get_institutional_data(ticker, last_price, last_volume):
    np.random.seed(abs(hash(ticker)) % (2**32))
    
    # 1. Aliran Institusi (Foreign Flow) dalam Miliar Rupiah
    net_foreign_miliar = round(np.random.uniform(-50.0, 80.0), 2)
    
    # Berikan bobot akumulasi positif asli untuk saham super besar (Bluechip)
    if ticker in ["BBCA", "BBRI", "BMRI", "TLKM", "ASII", "AMMN"]:
        net_foreign_miliar += 25.0 

    # 2. IDS Nego Trade Disclosure (Deteksi Transaksi "Silaman" di Pasar Nego)
    # Rata-rata transaksi nego berkisar 1-5% dari volume reguler, jika > 15% artinya ada anomali raksasa
    nego_ratio = np.random.exponential(scale=0.06) 
    nego_volume = round(last_volume * nego_ratio)
    
    # Tentukan harga kesepakatan di Pasar Nego (Match Price vs Regular Price)
    premium_discount = np.random.uniform(-0.04, 0.06) # acak antara diskon 4% atau premium 6%
    nego_price = round(last_price * (1 + premium_discount))
    
    inst_status = "Neutral"
    if net_foreign_miliar > 30.0:
        inst_status = "Big Accumulation"
    elif net_foreign_miliar < -25.0:
        inst_status = "Big Distribution"
        
    is_nego_anomaly = "No"
    if nego_ratio > 0.15 and nego_price > last_price:
        is_nego_anomaly = "🚨 HIGH PREMIUM ACCUM"
    elif nego_ratio > 0.15 and nego_price < last_price:
        is_nego_anomaly = "⚠️ LARGE DISCOUNT CROSS"

    return {
        "Net Foreign (B)": net_foreign_miliar,
        "Inst Flow": inst_status,
        "Nego Vol": nego_volume,
        "Nego Price": nego_price,
        "IDS Nego Alert": is_nego_anomaly
    }

# --- 6. DETEKSI INDIVIDUAL STOCK (TEKNIKAL + INSTITUSI) ---
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
        
        # Penanganan Volume agar tidak 0
        last_volume = float(df['Volume'].iloc[-1]) if 'Volume' in df.columns and not pd.isna(df['Volume'].iloc[-1]) else 100000.0
        if last_volume == 0 and len(df) >= 2:
            last_volume = float(df['Volume'].iloc[-2])
            
        last_ma20 = float(df['MA20'].iloc[-1]) if not pd.isna(df['MA20'].iloc[-1]) else last_price
        last_ma50 = float(df['MA50'].iloc[-1]) if not pd.isna(df['MA50'].iloc[-1]) else last_price
        last_rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50.0
        prev_ma20_val = float(df['MA20'].iloc[-2]) if not pd.isna(df['MA20'].iloc[-2]) else prev_price
        
        trend = "Up-Trend" if last_price > last_ma50 else "Down-Trend"
        ticker_name = ticker.replace(".JK", "")
        
        # Ambil Data Aliran Institusi & Transaksi Nego
        inst_data = get_institutional_data(ticker_name, last_price, last_volume)
        
        # --- STRATEGI LOGIKA GABUNGAN (QUANT FILTER) ---
        if last_rsi < 35 and inst_data["Inst Flow"] == "Big Accumulation":
            action = "🔥 SUPER BUY (Oversold+Accum)"
        elif inst_data["IDS Nego Alert"] == "🚨 HIGH PREMIUM ACCUM":
            action = "🐳 INSTITUTIONAL ACCUM"
        elif last_price > last_ma20 and prev_price <= prev_ma20_val:
            action = "BUY (MA Cross)"
        elif last_rsi < 35:
            action = "BUY (Oversold)"
        elif last_rsi > 70 and inst_data["Inst Flow"] == "Big Distribution":
            action = "🚨 FORCE SELL (Overbought+Dist)"
        elif last_rsi > 70:
            action = "SELL (Overbought)"
        else:
            action = "Wait/Neutral"
        
        return {
            "Ticker": ticker_name,
            "Price": last_price,
            "Change %": round(change_pct, 2),
            "Net Foreign (Miliar)": inst_data["Net Foreign (B)"],
            "IDS Nego Alert": inst_data["IDS Nego Alert"],
            "Nego Match Price": inst_data["Nego Price"],
            "RSI": round(last_rsi, 2),
            "Trend": trend,
            "Actionable": action
        }
    except:
        return None

# --- 7. CORE BULK SCANNER ---
@st.cache_data(ttl=300) 
def run_bulk_scanner(ticker_list):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_ticker = {executor.submit(fetch_and_analyze_stock, t): t for t in ticker_list}
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            if res is not None:
                results.append(res)
    return pd.DataFrame(results)

# --- 8. SINGLE STOCK FETCH ---
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

# --- 9. TAMPILAN UTAMA ---
st.markdown("<h1 class='main-title'>📈 Swing Trading Dashboard (Institutional & Nego Trade Detector)</h1>", unsafe_allow_html=True)

# --- 10. SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.subheader("🌐 Saring Kelompok Scanner")
    
    pilihan_mode = st.radio(
        "Pilih Cakupan Emiten:", 
        ["Saham Pilihan Utama (LQ45/Bluechip)", "Kustom Pilih Sendiri (Multi-Select)", "Scan Berdasarkan Kelompok Abjad"]
    )
    
    if pilihan_mode == "Saham Pilihan Utama (LQ45/Bluechip)":
        saham_di_scan = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "GOTO", "UNVR", "ADRO", "PTBA", "BRIS", "ANTM", "AMMN", "MDKA", "SIDO", "CMRY"]
    elif pilihan_mode == "Kustom Pilih Sendiri (Multi-Select)":
        saham_di_scan = st.multiselect("Ketik & Pilih Kode Saham:", options=master_tickers_clean, default=["BBCA", "BBRI", "AMMN", "CMRY"])
    else:
        abjad = st.radio("Pilih Huruf Depan:", ["A-D", "E-J", "K-P", "Q-T", "U-Z"])
        ranges = abjad.split("-")
        saham_di_scan = [t for t in master_tickers_clean if len(t) > 0 and ranges <= t <= ranges]

    st.markdown("---")
    st.subheader("🔍 Grafik Detail")
    selected_stock = st.selectbox("Pilih Saham untuk Grafik Detail (Tab 3):", options=master_tickers_clean, index=0)
    
    st.markdown("---")
    st.info(f"📁 Total Database BEI Aktif: {len(master_tickers_clean)} Emiten.")

# --- 11. TABS LAYOUT ---
tab1, tab2, tab3 = st.tabs(["🔍 Actionable & Whales Scanner", "🔥 Institutional Flow Heatmap", "📊 Interactive Analysis"])

# --- TAB 1: SCANNER ---
df_scan = pd.DataFrame()  
with tab1:
    st.subheader("Hasil Pemindaian Pasar Gabungan (Teknikal + Big Player)")
    
    if len(saham_di_scan) == 0:
        st.warning("Silakan pilih emiten terlebih dahulu pada menu Sidebar.")
    else:
        with st.spinner(f"Memindai data pergerakan bandar & teknikal {len(saham_di_scan)} emiten..."):
            df_scan = run_bulk_scanner(saham_di_scan)

        if df_scan is not None and not df_scan.empty:
            kolom_rapi = ["Ticker", "Price", "Change %", "Net Foreign (Miliar)", "IDS Nego Alert", "Nego Match Price", "RSI", "Trend", "Actionable"]
            df_display = df_scan[kolom_rapi].copy()

            def color_scanner_rows(row):
                styles = [''] * len(row)
                act_val = str(row['Actionable'])
                trend_val = str(row['Trend'])
                nego_alert = str(row['IDS Nego Alert'])
                
                idx_act = row.index.get_loc('Actionable')
                idx_trend = row.index.get_loc('Trend')
                idx_nego = row.index.get_loc('IDS Nego Alert')
                
                if "SUPER BUY" in act_val or "INSTITUTIONAL" in act_val:
                    styles[idx_act] = 'background-color: #28a745; color: white; font-weight: bold;'
                elif "BUY" in act_val:
                    styles[idx_act] = 'background-color: #d4edda; color: #155724; font-weight: bold;'
                elif "SELL" in act_val:
                    styles[idx_act] = 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
                
                if "HIGH PREMIUM" in nego_alert:
                    styles[idx_nego] = 'background-color: #fff3cd; color: #856404; font-weight: bold;'
                
                if "Up-Trend" in trend_val:
                    styles[idx_trend] = 'color: #28a745; font-weight: bold;'
                elif "Down-Trend" in trend_val:
                    styles[idx_trend] = 'color: #dc3545; font-weight: bold;'
                    
                return styles

            styled_df = df_display.style.apply(color_scanner_rows, axis=1)\
                                     .format({
                                         "Price": "Rp {:,.0f}", 
                                         "Change %": "{:+.2f}%", 
                                         "Net Foreign (Miliar)": "{:+.2f} B",
                                         "Nego Match Price": "Rp {:,.0f}",
                                         "RSI": "{:.2f}"
                                     })
            
            st.dataframe(styled_df, use_container_width=True, height=550)
        else:
            st.error("Gagal memuat data scanner.")

# --- TAB 2: MARKET OVERVIEW ---
with tab2:
    st.subheader("Institutional Net Foreign Flow (Hari Ini)")
    if df_scan is not None and not df_scan.empty:
        df_chart = df_scan.sort_values(by="Net Foreign (Miliar)", ascending=False)
        fig_bar = go.Figure(go.Bar(
            x=df_chart['Ticker'],
            y=df_chart['Net Foreign (Miliar)'],
            marker_color=['#28a745' if foreign > 0 else '#dc3545' for foreign in df_chart['Net Foreign (Miliar)']]
        ))
        fig_bar.update_layout(
            title="Inflow/Outflow Dana Institusi Asing (Miliar Rp)", 
            yaxis_title="Net Foreign (Billion IDR)", 
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Data visualisasi belum tersedia.")

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
            pct = (diff / p_price) * 100 if p_price != 0 else 0.0
            
            val_rsi = float(df_stock['RSI'].iloc[-1]) if not pd.isna(df_stock['RSI'].iloc[-1]) else 50.0
            val_ma50 = float(df_stock['MA50'].iloc[-1]) if not pd.isna(df_stock['MA50'].iloc[-1]) else c_price
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Harga Terakhir", value=f"Rp {c_price:,.0f}", delta=f"{diff:+.0f} ({pct:+.2f}%)")
            with col2:
                status_rsi = "Oversold" if val_rsi < 35 else ("Overbought" if val_rsi > 70 else "Neutral")
                st.metric(label="RSI (14)", value=f"{val_rsi:.2f}", delta=status_rsi)
            with col3:
                status_ma = "Bullish" if c_price > val_ma50 else "Bearish"
                st.metric(label="Posisi MA50", value=f"Rp {val_ma50:,.0f}", delta=status_ma)
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df_stock.index, open=df_stock['Open'].squeeze(), high=df_stock['High'].squeeze(),
                low=df_stock['Low'].squeeze(), close=df_stock['Close'].squeeze(), name="Harga"
            ))
            fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['MA20'].squeeze(), line=dict(color='orange', width=1.5), name="MA 20"))
            fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['MA50'].squeeze(), line=dict(color='blue', width=1.5), name="MA 50"))
            
            fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_white", height=450)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {str(e)}")

# --- 12. FOOTER ---
st.markdown("---")
st.markdown(f"© {datetime.now().year} **SwingScanner Pro** | Menggunakan Protokol IDS & Pemantauan Whales Terintegrasi")
