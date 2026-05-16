import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Swing Trading Scanner", layout="wide", page_icon="📈")

# --- CUSTOM CSS (Tampilan Bersih & Modern) ---
st.markdown("""
    <style>
    .stApp { background-color: #FAFAFA; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; }
    .main-title { color: #1E1E1E; font-weight: 800; padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER DATA EMITEN (Fallback jika CSV tidak ada) ---
try:
    tickers = pd.read_csv('saham_list.csv')['Ticker'].tolist()
except:
    # Default top saham LQ45 untuk testing
    tickers = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "UNVR.JK", "ADRO.JK", "PTBA.JK"]

# --- FUNGSI CACHING UNTUK AMBIL DATA SATUAN (Untuk Tab 3 Grafik) ---
@st.cache_data(ttl=600)  # Cache 10 menit untuk analisis detail
def get_single_stock_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty or len(df) < 50:
            return None
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        return df
    except:
        return None

# --- FUNGSI BULK SCANNER (Tab 1) ---
@st.cache_data(ttl=1800)  # Cache 30 menit untuk bulk scanning agar hemat kuota & cepat
def scan_saham(ticker_list):
    results = []
    for ticker in ticker_list:
        try:
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)
            if len(df) < 50: continue
            
            # Hitung Indikator
            df['MA20'] = ta.sma(df['Close'], length=20)
            df['MA50'] = ta.sma(df['Close'], length=50)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            # Ambil nilai terakhir & sebelumnya
            last_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            change_pct = ((last_price - prev_price) / prev_price) * 100
            
            last_rsi = float(df['RSI'].iloc[-1])
            last_ma20 = float(df['MA20'].iloc[-1])
            last_ma50 = float(df['MA50'].iloc[-1])
            prev_ma20 = float(df['MA20'].iloc[-2])
            
            # Logika Trend
            trend = "Up-Trend" if last_price > last_ma50 else "Down-Trend"
            
            # Logika Sinyal (Actionable)
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

# --- TAMPILAN UTAMA ---
st.markdown("<h1 class='main-title'>📈 Swing Trading Dashboard</h1>", unsafe_allow_html=True)

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # Pencarian Saham Spesifik untuk Tab Analisis
    st.subheader("Analisis Saham Individual")
    clean_tickers = [t.replace(".JK", "") for t in tickers]
    selected_stock = st.selectbox("Pilih Saham untuk Grafik:", clean_tickers, index=0)
    
    st.markdown("---")
    st.subheader("Filter Scanner (Tab 1)")
    strategi = st.multiselect("Strategi Aktif:", 
                             ["MA 20 Cross", "RSI Oversold", "RSI Overbought"],
                             default=["MA 20 Cross", "RSI Oversold"])
    
    min_rsi_filter = st.slider("Batas Minimum RSI", 0, 100, 30)

# --- LAYOUT TABS ---
tab1, tab2, tab3 = st.tabs(["🔍 Actionable Scanner", "🔥 Market Heatmap", "📊 Interactive Analysis"])

# --- TAB 1: SCANNER ---
with tab1:
    st.subheader("Hasil Pemindaian Pasar Harian")
    
    with st.spinner("Memproses data pasar dari Yahoo Finance..."):
        df_scan = scan_saham(tickers)

    if not df_scan.empty:
        # Fungsi styling baris tabel
        def color_rows(val):
            if "BUY" in str(val): return 'background-color: #d4edda; color: #155724; font-weight: bold;'
            if "SELL" in str(val): return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
            if "Up-Trend" in str(val): return 'color: #28a745; font-weight: bold;'
            if "Down-Trend" in str(val): return 'color: #dc3545; font-weight: bold;'
            return ''

        # Menerapkan style dan format angka tampilan tabel agar rapi
        styled_df = df_scan.style.applymap(color_rows, subset=['Actionable', 'Trend'])\
                                 .format({"Price": "Rp {:,.0f}", "Change %": "{:+.2f}%", "RSI": "{:.2f}"})
        
        st.dataframe(styled_df, use_container_width=True, height=450)
        st.caption("💡 *Tip: Gunakan pencarian di sidebar atau klik nama kolom tabel untuk mengurutkan data.*")
    else:
        st.error("Gagal memuat data scanner. Periksa koneksi internet atau daftar emiten Anda.")

# --- TAB 2: HEATMAP ---
with tab2:
    st.subheader("Market Performance Overview")
    st.info("Fitur Market Heatmap menggunakan Treemap untuk visualisasi performa sektor.")
    
    # Contoh implementasi sederhana Chart Interaktif Plotly di Tab 2
    if not df_scan.empty:
        fig_pie = go.Figure(go.Bar(
            x=df_scan['Ticker'],
            y=df_scan['Change %'],
            marker_color=['#28a745' if change > 0 else '#dc3545' for change in df_scan['Change %']]
        ))
        fig_pie.update_layout(title="Perubahan Harga Saham (%) Hari Ini", yaxis_title="Persentase Perubahan", template="plotly_white")
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 3: INTERACTIVE ANALYSIS (Grafik ala TradingView) ---
with tab3:
    st.subheader(f"Analisis Teknikal Mendalam: {selected_stock}")
    
    # Ambil data lengkap untuk saham yang dipilih di sidebar
    ticker_jk = f"{selected_stock}.JK"
    df_stock = get_single_stock_data(ticker_jk)
    
    # PENGAMAN UTAMA: Pastikan df_stock tidak None, tidak kosong, dan punya data yang cukup
    if df_stock is not None and not df_stock.empty and len(df_stock) >= 2:
        try:
            # Mengambil baris terakhir dan sebelum terakhir dengan aman
            last_row = df_stock.iloc[-1]
            prev_row = df_stock.iloc[-2]
            
            # Pengaman tambahan: pastikan kolom 'Close' ada nilainya dan tidak NaN
            if pd.notna(last_row['Close']) and pd.notna(prev_row['Close']):
                # Menggunakan item() atau mengambil nilai skalar secara aman dari pandas Series
                c_price = float(last_row['Close'].values) if hasattr(last_row['Close'], 'values') else float(last_row['Close'])
                p_price = float(prev_row['Close'].values) if hasattr(prev_row['Close'], 'values') else float(prev_row['Close'])
                
                diff = c_price - p_price
                pct = (diff / p_price) * 100
                
                # Mengambil nilai RSI dan MA50 secara aman
                rsi_val = float(last_row['RSI'].values) if hasattr(last_row['RSI'], 'values') else float(last_row['RSI'])
                ma50_val = float(last_row['MA50'].values) if hasattr(last_row['MA50'], 'values') else float(last_row['MA50'])
                ma20_val = float(last_row['MA20'].values) if hasattr(last_row['MA20'], 'values') else float(last_row['MA20'])
                
                # 1. Tampilkan Ringkasan Menggunakan st.metric
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Harga Terakhir", value=f"Rp {c_price:,.0f}", delta=f"{diff:+.0f} ({pct:+.2f}%)")
                with col2:
                    delta_rsi = "Oversold (<35)" if rsi_val < 35 else ("Overbought (>70)" if rsi_val > 70 else "Neutral")
                    st.metric(label="RSI (14)", value=f"{rsi_val:.2f}", delta=delta_rsi)
                with col3:
                    delta_ma = "Di atas MA50 (Bullish)" if c_price > ma50_val else "Di bawah MA50 (Bearish)"
                    st.metric(label="Posisi MA50", value=f"Rp {ma50_val:,.0f}", delta=delta_ma)
                
                # 2. Buat Grafik Candlestick Interaktif dengan Plotly
                fig = go.Figure()
                
                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=df_stock.index,
                    open=df_stock['Open'], high=df_stock['High'],
                    low=df_stock['Low'], close=df_stock['Close'],
                    name="Harga Saham"
                ))
                
                # Garis Moving Average 20 & 50
                fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['MA20'], line=dict(color='orange', width=1.5), name="MA 20"))
                fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['MA50'], line=dict(color='blue', width=1.5), name="MA 50"))
                
                # Atur Tampilan Grafik
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
            else:
                st.warning(f"Data harga terbaru untuk {selected_stock} tidak lengkap atau kosong di Yahoo Finance.")
                
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data grafik: {str(e)}")
    else:
        st.warning(f"⚠️ Gagal memuat data untuk {selected_stock}. Yahoo Finance kemungkinan membatasi request Anda atau emiten sedang disuspensi. Silakan coba pilih kode saham lain di sidebar.")
# --- FOOTER ---
st.markdown("---")
st.markdown(f"© {datetime.now().year} **SwingScanner Pro** | Menggunakan Streamlit Modern | Data Source: Yahoo Finance")
