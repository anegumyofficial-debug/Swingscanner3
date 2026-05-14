import streamlit as st
import pandas as pd
import plotly.express as px
import leafmap.foliumap as leafmap

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Infeksius Actio Dashboard",
    page_icon="🦠",
    layout="wide"
)

# --- CSS CUSTOM (Untuk Meniru Estetika) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_ some_html=True)

# --- SIDEBAR / NAVIGASI ---
with st.sidebar:
    st.title("🦠 Infeksius Actio")
    st.image("https://via.placeholder.com/150", caption="Logo Program") # Ganti dengan URL logo asli
    menu = st.radio(
        "Navigasi Utama",
        ["Dashboard Ringkasan", "Peta Sebaran", "Analisis Tren", "Informasi Penyakit"]
    )
    st.divider()
    st.info("Aplikasi ini digunakan untuk pemantauan data penyakit infeksius secara real-time.")

# --- MOCK DATA (Ganti dengan dataset asli Anda) ---
data = pd.DataFrame({
    'Wilayah': ['Jakarta', 'Bandung', 'Surabaya', 'Medan', 'Makassar'],
    'Kasus': [120, 85, 95, 60, 45],
    'Sembuh': [100, 70, 80, 50, 40],
    'lat': [-6.2088, -6.9175, -7.2575, 3.5952, -5.1476],
    'lon': [106.8456, 107.6191, 112.7521, 98.6722, 119.4327]
})

# --- LOGIKA HALAMAN ---

if menu == "Dashboard Ringkasan":
    st.header("📊 Ringkasan Data Infeksius")
    
    # Row 1: Metrik Utama
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Kasus", data['Kasus'].sum(), "+5% dari bulan lalu")
    col2.metric("Total Sembuh", data['Sembuh'].sum(), "82% Rate")
    col3.metric("Wilayah Terdampak", len(data), "Provinsi")

    st.divider()

    # Row 2: Visualisasi
    c1, c2 = st.columns([6, 4])
    with c1:
        st.subheader("Perbandingan Kasus per Wilayah")
        fig = px.bar(data, x='Wilayah', y='Kasus', color='Wilayah', template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.subheader("Proporsi Sembuh")
        fig_pie = px.pie(data, values='Sembuh', names='Wilayah', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

elif menu == "Peta Sebaran":
    st.header("🗺️ Peta Distribusi Geografis")
    
    # Integrasi Peta Menggunakan Leafmap
    m = leafmap.Map(center=[-2.5, 118], zoom=5)
    m.add_points_from_xy(
        data, 
        x="lon", 
        y="lat", 
        popups=["Wilayah", "Kasus"],
        layer_name="Titik Kasus"
    )
    m.to_streamlit(height=600)

elif menu == "Analisis Tren":
    st.header("📈 Analisis Tren Waktu")
    st.write("Fitur ini menampilkan perkembangan data dari waktu ke waktu.")
    # Contoh chart garis sederhana
    trend_data = pd.DataFrame({
        'Bulan': ['Jan', 'Feb', 'Mar', 'Apr'],
        'Kasus': [20, 45, 30, 65]
    })
    fig_line = px.line(trend_data, x='Bulan', y='Kasus', markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

else:
    st.header("ℹ️ Informasi & Edukasi")
    st.markdown("""
    ### Tentang Penyakit Infeksius
    Penyakit infeksius disebabkan oleh organisme seperti bakteri, virus, jamur, atau parasit. 
    Aplikasi ini bertujuan untuk:
    1. Memberikan transparansi data.
    2. Membantu pengambilan keputusan medis.
    3. Edukasi masyarakat luas.
    """)
