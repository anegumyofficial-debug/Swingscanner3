import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

# CSS agar kotak Summary (Bar Baru) terlihat profesional
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Tampilkan Bar Ringkasan (Metrics)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Saham", "6")
col2.metric("🟢 Siap Serok", "2")
col3.metric("🔴 Jual", "1")
col4.metric("⚪ Neutral", "3")

st.markdown("---")
st.write("Detail tabel akan muncul di bawah sini setelah data ditarik...")
