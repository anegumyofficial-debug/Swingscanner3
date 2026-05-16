import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Swing Trading Scanner", layout="wide", page_icon="📈")

# --- 2. CUSTOM CSS (Tampilan Bersih & Profesional) ---
st.markdown("""
    <style>
    .stApp { background-color: #FAFAFA; }
    div[data-testid="stMetricValue"] { font-size: 26px; font-weight: bold; }
    .main-title { color: #1E1E1E; font-weight: 800; padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MASTER DATA EMITEN (LQ45 Pasang Dropback Aman) ---
try:
    tickers = pd.read_csv('saham_list.csv')['Ticker'].tolist()
except:
    tickers = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "UNVR.JK", "ADRO.JK", "PTBA.JK"]

# --- 4. FUNGSI UTAS UNTUK MEMBERSIHKAN MULTI-INDEX YAHOO FINANCE ---
def clean_yf_dataframe(df):
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)
    return df

# --- 5. FUNGSI CACHING UNTUK GRAPH DETAIL (Tab 3) ---
@st.cache_data(ttl=600)
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

# --- 6. FUNGSI CACHING UNTUK BULK SCANNER (Tab 1) ---
@st.cache_data(ttl=1800)
def scan_saham(ticker_list):
    results = []
    for ticker in ticker_list:
        try:
            formatted_ticker = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
            df = yf.download(formatted_ticker, period="6mo", interval="1d", progress=False)
            df = clean_yf_dataframe(df)
            
            if df is None or len(df) < 50: 
                continue
            
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
            
            results.append({
                "Ticker": ticker.replace(".JK", ""),
                "Price": last_price,
                "Change %": round(change_pct, 2),
                "RSI": round(last_rsi, 2),
                "Trend": trend,
                "Actionable": action
            })
        except:
            continue
    return pd.DataFrame(results)

# --- 7. TAMPILAN UTAMA & HEADER ---
st.markdown("<h1 class='main-title'>📈 Swing Trading Dashboard</h1>", unsafe_allow_html=True)

# --- 8. SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.subheader("Analisis Saham Individual")
    clean_tickers = [t.replace(".JK", "") for t in tickers]
    selected_stock = st.selectbox("Pilih Saham untuk Grafik:", clean_tickers, index=0)
    
    st.markdown("---")
    st.subheader("Filter Scanner (Tab 1)")
    strategi = st.multiselect("Strategi Aktif:", 
                             ["MA 20 Cross", "RSI Oversold", "RSI Overbought"],
                             default=["MA 20 Cross", "RSI Oversold"])
    min_rsi_filter = st.slider("Batas Minimum RSI", 0, 100, 30)

# --- 9. DEFINISI LAYOUT TABS ---
tab1, tab2, tab3 = st.tabs(["🔍 Actionable Scanner", "🔥 Market Heatmap", "📊 Interactive Analysis"])

# --- TAB 1: SCANNER UTAMA ---
with tab1:
    st.subheader("Hasil Pemindaian Pasar Harian")
    
    with st.spinner("Memproses data pasar dari Yahoo Finance..."):
        df_scan = scan_saham(tickers)

    if df_scan is not None and not df_scan.empty:
        # PANDAS 2.1+ REPLACEMENT: Menggunakan fungsi .map() sebagai pengganti .applymap()
        def color_rows(val):
            val_str = str(val)
            if "BUY" in val_str: return 'background-color: #d4edda; color: #155724; font-weight: bold;'
            if "SELL" in val_str: return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
            if "Up-Trend" in val_str: return 'color: #28a745; font-weight: bold;'
            if "Down-Trend" in val_str: return 'color: #dc3545; font-weight: bold;'
            return ''

        # Menggunakan .map() agar kompatibel dengan versi Pandas terbaru di server Streamlit
        styled_df = df_scan.style.map(color_rows, subset=['Actionable', 'Trend'])\
                                 .format({"Price": "Rp {:,.0f}", "Change %": "{:+.2f}%", "RSI": "{:.2f}"})
        
        st.dataframe(styled_df, use_container_width=True, height=450)
        st.caption("💡 *Tip: Gunakan kolom pencarian di sebelah kanan atas tabel untuk menyaring emiten.*")
    else:
        st.error("Gagal memuat data scanner. Periksa koneksi internet atau daftarkan emiten di file csv dengan benar.")

# --- TAB 2: MARKET OVERVIEW ---
with tab2:
    st.subheader("Market Performance Overview")
    st.info("Fitur Market Heatmap menggunakan diagram batang interaktif untuk melihat performa pergerakan harga.")
    
    if df_scan is not None and not df_scan.empty:
        fig_bar = go.Figure(go.Bar(
            x=df_scan['Ticker'],
            y=df_scan['Change %'],
            marker_color=['#28a745' if change > 0 else '#dc3545' for change in df_scan['Change %']]
        ))
        fig_bar.update_layout(title="Perubahan Harga Saham (%) Hari Ini", yaxis_title="Persentase Perubahan", template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Data visualisasi heatmap belum tersedia karena unduhan bulk data kosong.")

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
                xaxis_title="Tanggal",
                yaxis_title="Harga (IDR)",
                xaxis_rangeslider_visible=False,
                template="plotly_white",
                height=500,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Terjadi kesalahan pemrosesan kolom data: {str(e)}")
    else:
        st.warning(f"⚠️ Yahoo Finance tidak mengembalikan data untuk {selected_stock}. Silakan coba pilih kode saham lain.")

# --- 10. FOOTER ---
st.markdown("---")
st.markdown(f"© {datetime.now().year} **SwingScanner Pro** | Menggunakan Streamlit Modern | Data Source: Yahoo Finance")
