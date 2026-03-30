import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import requests
import time

# --- 1. CONFIG GIAO DIỆN ---
st.set_page_config(page_title='Kevin Elite Finance', layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #030406; color: #e0e0e0; }
    .stButton button {
        background: linear-gradient(90deg, #1db954 0%, #191414 100%) !important;
        border: none !important; color: white !important;
        border-radius: 10px !important; height: 45px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG CACHE & AI ---
@st.cache_data(ttl=600)
def get_stock_data(symbol):
    ticker_yf = f"{symbol}.HM"
    df = yf.download(ticker_yf, period="3mo", interval="1d", progress=False)
    return df

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
    return "🚨 Vệ tinh bận, thử lại sau 1 phút nhé!"

# --- 3. QUẢN LÝ THỜI GIAN NHẤN NÚT (TOAST) ---
if 'last_request' not in st.session_state:
    st.session_state.last_request = 0

# --- 4. GIAO DIỆN CHÍNH ---
st.sidebar.title("🛡️ KEVIN ELITE")
# Định nghĩa ticker ở đây để không bị lỗi NameError
ticker_input = st.sidebar.text_input("Nhập mã (VD: FPT, HPG):", "").upper()

if not ticker_input:
    st.markdown('<div style="text-align:center; padding-top:150px; color:#888;"><h1>📈 KEVIN FINANCE ENGINE</h1><p>Hệ thống đã sẵn sàng. Nhập mã để bắt đầu soi lệnh.</p></div>', unsafe_allow_html=True)
else:
    if st.button(f"🔍 PHÂN TÍCH {ticker_input}"):
        current_time = time.time()
        elapsed = current_time - st.session_state.last_request
        
        # Nếu nhấn quá nhanh (dưới 20s) thì hiện Toast báo chờ
        if elapsed < 20:
            remaining = int(20 - elapsed)
            st.toast(f"Kevin ơi, chờ {remaining}s nữa để né Google quét nhé!", icon="🛰️")
        else:
            st.session_state.last_request = current_time
            with st.spinner('Đang kết nối vệ tinh Google Finance...'):
                try:
                    df = get_stock_data(ticker_input)
                    if not df.empty:
                        # Vẽ biểu đồ Plotly
                        fig = go.Figure(data=[go.Candlestick(
                            x=df.index, open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'],
                            increasing_line_color='#1db954', decreasing_line_color='#e91e63'
                        )])
                        fig.update_layout(template='plotly_dark', height=450, title=f"Biểu đồ 3 tháng mã {ticker_input}")
                        st.plotly_chart(fig, use_container_width=True)

                        # AI Phân tích
                        lp = float(df['Close'].iloc[-1])
                        st.session_state.anal = safe_ai(f"Mã {ticker_input}, giá {lp:,.0f}đ. Hãy phân tích kỹ thuật ngắn hạn.")
                        st.toast("Dữ liệu đã về, AI đang phản hồi!", icon="✅")
                    else:
                        st.error("❌ Google báo giới hạn (Limit). Kevin hãy đợi 5 phút nhé!")
                except Exception as e:
                    st.error(f"🚨 Lỗi: {str(e)}")

    if 'anal' in st.session_state:
        st.subheader("🚀 AI Đánh Giá")
        st.info(st.session_state.anal)

    # TRỢ LÝ CHAT
    q = st.chat_input(f"Hỏi thêm về {ticker_input}...")
    if q:
        st.session_state.chat = safe_ai(f"Mã {ticker_input}: {q}")
    
    if 'chat' in st.session_state:
        st.subheader("💬 Trợ Lý")
        st.success(st.session_state.chat)
        if st.button("🗑️ XOÁ CHAT"):
            if 'chat' in st.session_state: del st.session_state.chat
            st.rerun()
