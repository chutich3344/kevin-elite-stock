import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests
import time

# --- 1. CONFIG ---
st.set_page_config(page_title='Kevin Elite Finance', layout="wide")

# --- 2. HÀM LẤY DATA CÓ CACHE (ĐỂ NÉ LIMIT) ---
@st.cache_data(ttl=600) # Lưu dữ liệu trong 10 phút
def get_stock_data(ticker):
    ticker_yf = f"{ticker}.HM"
    # Giả lập trình duyệt để né bị Yahoo chặn
    dat = yf.Ticker(ticker_yf)
    df = dat.history(period="3mo", interval="1d")
    return df

# --- 3. HỆ THỐNG AI ---
raw_keys = st.secrets.get("gemini_keys", [])
LIST_KEYS = [k.strip().replace('"', '').replace("'", "") for k in raw_keys if k.strip()]

def safe_ai(prompt):
    if not LIST_KEYS: return "🚨 Check Secrets!"
    k = LIST_KEYS[0]
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={k}"
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
    except: pass
    return "🚨 AI đang bận, thử lại sau 1 phút."

# --- 4. GIAO DIỆN ---
st.sidebar.title("🛡️ KEVIN ELITE")
ticker = st.sidebar.text_input("Nhập mã (VD: FPT, HPG):", "").upper()

if ticker:
    if st.button(f"🔍 PHÂN TÍCH {ticker}"):
        with st.spinner('Đang kết nối vệ tinh...'):
            try:
                df = get_stock_data(ticker)
                if not df.empty:
                    # Vẽ biểu đồ
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'],
                        increasing_line_color='#1db954', decreasing_line_color='#e91e63'
                    )])
                    fig.update_layout(template='plotly_dark', height=450, title=f"Dữ liệu 3 tháng mã {ticker}")
                    st.plotly_chart(fig, use_container_width=True)

                    # AI Phân tích
                    lp = float(df['Close'].iloc[-1])
                    st.session_state.anal = safe_ai(f"Mã {ticker}, giá {lp:,.0f}đ. Hãy phân tích kỹ thuật.")
                else:
                    st.error("❌ Google đang chặn IP. Kevin đợi 5-10 phút rồi thử lại nhé!")
            except Exception as e:
                st.error(f"🚨 Lỗi: {str(e)}")

    if 'anal' in st.session_state:
        st.info(st.session_state.anal)
