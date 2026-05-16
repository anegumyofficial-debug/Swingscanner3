import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime

# --- TAB 1: SCANNER UTAMA ---
with tab1:
    st.subheader("Hasil Pemindaian Pasar Harian")
    
    with st.spinner("Memproses data pasar dari Yahoo Finance..."):
        df_scan = scan_saham(tickers)

    if not df_scan.empty:
        # Fungsi styling warna untuk baris tabel
        def color_rows(val):
            if "BUY" in str(val): return 'background-color: #d4edda; color: #155724; font-weight: bold;'
            if "SELL" in str(val): return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
            if "Up-Trend" in str(val): return 'color: #28a745; font-weight: bold;'
            if "Down-Trend" in str(val): return 'color: #dc3545; font-weight: bold;'
            return ''

        # Terapkan styling warna dan format angka rupiah/persen agar rapi
        styled_df = df_scan.style.applymap(color_rows, subset=['Actionable', 'Trend'])\
                                 .format({"Price": "Rp {:,.0f}", "Change %": "{:+.2f}%", "RSI": "{:.2f}"})
        
        st.dataframe(styled_df, use_container_width=True, height=450)
        st.caption("💡 *Tip: Gunakan kolom pencarian di sidebar atau klik nama kolom tabel untuk mengurutkan data.*")
    else:
        st.error("Gagal memuat data scanner. Periksa koneksi internet atau daftar emiten Anda.")

# --- TAB 2: MARKET OVERVIEW ---
with tab2:
    st.subheader("Market Performance Overview")
    st.info("Fitur Market Heatmap menggunakan diagram batang interaktif untuk melihat performa pergerakan harga.")
    
    if not df_scan.empty:
        # Membuat visualisasi bar chart sederhana dari data scanner menggunakan Plotly
        fig_bar = go.Figure(go.Bar(
            x=df_scan['Ticker'],
            y=df_scan['Change %'],
            marker_color=['#28a745' if change > 0 else '#dc3545' for change in df_scan['Change %']]
        ))
        fig_bar.update_layout(title="Perubahan Harga Saham (%) Hari Ini", yaxis_title="Persentase Perubahan", template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)

# --- TAB 3: INTERACTIVE ANALYSIS (Grafik Candle dengan Proteksi Anti-Crash) ---
with tab3:
    st.subheader(f"Analisis Teknikal Mendalam: {selected_stock}")
    
    ticker_jk = f"{selected_stock}.JK"
    df_stock = get_single_stock_data(ticker_jk)
    
    # Blok Pengaman Utama: Menghindari error layar merah (TypeError) jika data kosong
    if df_stock is not None and not df_stock.empty and len(df_stock) >= 2:
        try:
            last_row = df_stock.iloc[-1]
            prev_row = df_stock.iloc[-2]
            
            if pd.notna(last_row['Close']) and pd.notna(prev_row['Close']):
                # Konversi data ke tipe float skalar dengan aman (kompatibel Multi-index atau Single-index)
                c_price = float(last_row['Close'].values) if hasattr(last_row['Close'], 'values') else float(last_row['Close'])
                p_price = float(prev_row['Close'].values) if hasattr(prev_row['Close'], 'values') else float(prev_row['Close'])
                
                diff = c_price - p_price
                pct = (diff / p_price) * 100
                
                rsi_val = float(last_row['RSI'].values) if hasattr(last_row['RSI'], 'values') else float(last_row['RSI'])
                ma50_val = float(last_row['MA50'].values) if hasattr(last_row['MA50'], 'values') else float(last_row['MA50'])
                
                # A. Menampilkan Ringkasan Indikator Menggunakan Kotak st.metric
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Harga Terakhir", value=f"Rp {c_price:,.0f}", delta=f"{diff:+.0f} ({pct:+.2f}%)")
                with col2:
                    delta_rsi = "Oversold (<35)" if rsi_val < 35 else ("Overbought (>70)" if rsi_val > 70 else "Neutral")
                    st.metric(label="RSI (14)", value=f"{rsi_val:.2f}", delta=delta_rsi)
                with col3:
                    delta_ma = "Di atas MA50 (Bullish)" if c_price > ma50_val else "Di bawah MA50 (Bearish)"
                    st.metric(label="Posisi MA50", value=f"Rp {ma50_val:,.0f}", delta=delta_ma)
                
                # B. Membuat Grafik Candlestick Interaktif Plotly
                fig = go.Figure()
                
                # Komponen Candlestick utama
                fig.add_trace(go.Candlestick(
                    x=df_stock.index,
                    open=df_stock['Open'], high=df_stock['High'],
                    low=df_stock['Low'], close=df_stock['Close'],
                    name="Harga Saham"
                ))
                
                # Komponen Garis Moving Average overlay
                fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['MA20'], line=dict(color='orange', width=1.5), name="MA 20"))
                fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock['MA50'], line=dict(color='blue', width=1.5), name="MA 50"))
                
                fig.update_layout(
                    title=f"Grafik Historis {selected_stock} (1 Tahun Terakhir)",
                    xaxis_title="Tanggal",
                    yaxis_title="Harga (IDR)",
                    xaxis_rangeslider_visible=False,  # Mematikan range-slider agar chart tidak sempit
                    template="plotly_white",
                    height=500,
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Data harga terbaru untuk {selected_stock} tidak lengkap di Yahoo Finance.")
                
        except Exception as e:
            st.error(f"Terjadi kesalahan teknis saat merender grafik: {str(e)}")
    else:
        st.warning(f"⚠️ Gagal memuat data untuk {selected_stock}. Batasan request dari Yahoo Finance atau emiten sedang libur/suspensi. Silakan pilih kode saham lain di sidebar.")

# --- 9. FOOTER ---
st.markdown("---")
st.markdown(f"© {datetime.now().year} **SwingScanner Pro** | Menggunakan Streamlit Modern | Data Source: Yahoo Finance")
