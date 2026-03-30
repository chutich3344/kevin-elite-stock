import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import random
import time
import streamlit.components.v1 as components
from vnstock import *

# --- 1. CẤU HÌNH & CSS VŨ TRỤ (OCD APPROVED) ---
st.set_page_config(page_title='Kevin TV Elite', layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
    .stApp { background-color: #030406; font-family: 'Inter', sans-serif; }
    .stButton button {
        background: linear-gradient(90deg, #6c3483 0%, #a569bd 100%) !important;
        border: none !important; color: white !important; font-weight: 600 !important;
        height: 52px !important; border-radius: 12px !important; width: 100% !important;
        transition: 0.3s ease;
    }
    div[data-testid="stInfo"] {
        background: rgba(13, 17, 23, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important; padding: 25px !important;
        min-height: 350px !important; color: #ccd6f6 !important;
    }
    #spaceBtn {
        position: fixed; bottom: 35px; right: 35px; z-index: 9999;
        width: 85px; height: 85px; background: rgba(0,0,0,0.7) !important;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        text-decoration: none !important; cursor: pointer; border: 1px solid rgba(165, 105, 189, 0.3);
    }
    .center-planet { font-size: 35px; z-index: 2; }
    .orbiting-ship { position: absolute; font-size: 20px; animation: rotateShips 6s linear infinite; }
    @keyframes rotateShips {
        0% { transform: rotate(0deg) translate(42px) rotate(0deg); }
        100% { transform: rotate(360deg) translate(42px) rotate(-360deg); }
    }
</style>
<a href="#" id="spaceBtn">
    <div class="orbiting-ship" style="animation-delay: 0s;">🚀</div>
    <div class="orbiting-ship" style="animation-delay: -2s;">🛸</div>
    <div class="orbiting-ship" style="animation-delay: -4s;">✈️</div>
    <div class="center-planet">🌎</div>
</a>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG VỆ TINH GEMINI ---
LIST_KEYS = st.secrets.get("gemini_keys", [])

def safe_ai(prompt):
    if not LIST_KEYS: return "🚨 Lỗi: Chưa cấu hình gemini_keys trong Secrets!"
    shuffled = list(LIST_KEYS).copy()
    random.shuffle(shuffled)
    
    safety = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]

    for k in shuffled:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={k}"
        try:
            res = requests.post(url, json={
                "contents": [{"parts": [{"text": prompt}]}],
                "safetySettings": safety
            }, timeout=15)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
        except: continue
    return "🚨 Vệ tinh bận (Lỗi kết nối Google), Kevin thử lại nhé!"

# --- 3. GIAO DIỆN CHÍNH ---
st.sidebar.title("🛡️ KEVIN TV ELITE")
ticker_input = st.sidebar.text_input("Nhập mã (VD: VIC, FPT):", "VIC").upper()
ticker_list = [t.strip() for t in ticker_input.split(",") if t.strip()]

if not ticker_list:
    st.markdown('<div style="text-align:center; padding-top:100px; color:white;"><h1>🌌 KEVIN TRADINGVIEW</h1><p>Nhập mã tại Sidebar để bắt đầu.</p></div>', unsafe_allow_html=True)
else:
    # Tabs cho nhiều mã
    tabs = st.tabs([f"📊 {t}" for t in ticker_list])
    for i, ticker in enumerate(ticker_list):
        with tabs[i]:
            tv_html = f"""
            <div style="height:550px;">
              <div id="tv_{ticker}" style="height:550px;"></div>
              <script src="https://s3.tradingview.com/tv.js"></script>
              <script>
              new TradingView.widget({{"autosize": true, "symbol": "HOSE:{ticker}", "interval": "D", "theme": "dark", "locale": "vi_VN", "container_id": "tv_{ticker}"}});
              </script>
            </div>
            """
            components.html(tv_html, height=550)

    st.divider()
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown('<h3 style="color:white;">🚀 Phân Tích Kỹ Thuật</h3>', unsafe_allow_html=True)
        if st.button("QUÉT TÍN HIỆU AI"):
            with st.spinner('Đang lấy dữ liệu thị trường...'):
                try:
                    df = stock_historical_data(symbol=ticker_list[0], 
                                            start_date="2025-01-01", 
                                            end_date=datetime.now().strftime('%Y-%m-%d'), 
                                            resolution='1D', type='stock')
                    if not df.empty:
                        lp = df['close'].iloc[-1]
                        st.session_state.anal = safe_ai(f"Mã {ticker_list[0]}, giá hiện tại {lp:,.0f} VNĐ. Phân tích kỹ thuật ngắn hạn.")
                    else:
                        st.session_state.anal = "❌ Không lấy được dữ liệu. Kiểm tra lại mã."
                except Exception as e:
                    st.session_state.anal = f"❌ Lỗi vnstock: {str(e)}"
        st.info(st.session_state.get('anal', "Đang đợi lệnh..."))

    with col_r:
        st.markdown('<h3 style="color:white;">💬 Trợ Lý Trading</h3>', unsafe_allow_html=True)
        q = st.chat_input("Hỏi Gemini về mã này...")
        if q: 
            st.session_state.chat = safe_ai(f"Mã {ticker_list[0]}: {q}")
        st.info(st.session_state.get('chat', "Sẵn sàng trả lời..."))
