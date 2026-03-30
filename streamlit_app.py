import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import random

# --- 1. CONFIG GIAO DIỆN ---
st.set_page_config(page_title='Kevin Elite Finance', layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #030406; color: #e0e0e0; }
    .stButton button {
        background: linear-gradient(90deg, #1db954 0%, #191414 100%) !important;
        border: none !important; color: white !important;
        border-radius: 10px !important; height: 45px !important; width: 100% !important;
    }
    div[data-testid="stMetricValue"] { color: #1db954 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG AI ---
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
    return "🚨 Vệ tinh bận do quét quá nhanh, Kevin đợi 1 phút nhé!"

# --- 3. APP CHÍNH ---
st.sidebar.title("🛡️ KEVIN ELITE")
ticker_raw = st.sidebar.text_input("Nhập mã (VD: FPT, HPG, VIC):", "").upper()

if not ticker_raw:
    st.markdown('<div style="text-align:center; padding-top:150px; color:#888;"><h1>📈 GOOGLE FINANCE ENGINE</h1><p>Hệ thống dùng dữ liệu thời gian thực từ Google. Nhập mã để bắt đầu.</p></div>', unsafe_allow_html=True)
else:
    ticker_yf = f"{ticker_raw}.HM"
    
    # NÚT BẤM KÍCH HOẠT TẤT CẢ
    if st.button(f"🔍 PHÂN TÍCH MÃ {ticker_raw}"):
        with st.spinner('Đang kết nối vệ tinh Google Finance...'):
            try:
                # Lấy dữ liệu 3 tháng gần nhất để vẽ chart đẹp
                df = yf.download(ticker_yf, period="3mo", interval="1d")
                
                if not df.empty:
                    # 1. VẼ CHART PLOTLY
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index,
                        open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'],
                        increasing_line_color='#1db954', decreasing_line_color='#e91e63'
                    )])
                    fig.update_layout(title=f'Biểu đồ giá {ticker_raw}', template='plotly_dark', height=500)
                    st.plotly_chart(fig, use_container_width=True)

                    # 2. HIỂN THỊ CHỈ SỐ NHANH
                    lp = float(df['Close'].iloc[-1])
                    change = lp - float(df['Close'].iloc[-2])
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Giá hiện tại", f"{lp:,.0f}đ", f"{change:,.0f}đ")
                    
                    # 3. GỌI AI PHÂN TÍCH
                    st.session_state.anal = safe_ai(f"Mã {ticker_raw}, giá {lp:,.0f}đ. Dữ liệu 3 tháng qua có xu hướng { 'tăng' if change > 0 else 'giảm' }. Hãy phân tích kỹ thuật ngắn hạn.")
                else:
                    st.error(f"❌ Không tìm thấy mã {ticker_raw} hoặc đang bị giới hạn truy cập (Rate Limit).")
            except Exception as e:
                st.error(f"🚨 Lỗi hệ thống: {str(e)}")

    st.divider()
    if 'anal' in st.session_state:
        st.subheader("🚀 AI Đánh Giá")
        st.info(st.session_state.anal)

    # TRỢ LÝ CHAT
    q = st.chat_input(f"Hỏi thêm về mã {ticker_raw}...")
    if q:
        st.session_state.chat = safe_ai(f"Mã {ticker_raw}: {q}")
    
    if 'chat' in st.session_state:
        st.subheader("💬 Trợ Lý")
        st.success(st.session_state.chat)
        if st.button("🗑️ XOÁ CHAT"):
            del st.session_state.chat
            st.rerun()
