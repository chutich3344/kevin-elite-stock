import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import requests
import random
import time
import streamlit.components.v1 as components

# --- 1. CẤU HÌNH & CSS VŨ TRỤ (OCD APPROVED) ---
st.set_page_config(page_title='Kevin TV Elite', layout="wide")

CSS_CODE = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
    .stApp { background-color: #030406; font-family: 'Inter', sans-serif; }
    .tier-title { font-size: 1.4rem; font-weight: 800; color: #ffffff; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
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
    #ship1 { animation-delay: 0s; } #ship2 { animation-delay: -2s; } #ship3 { animation-delay: -4s; }
    @keyframes rotateShips {
        0% { transform: rotate(0deg) translate(42px) rotate(0deg); }
        100% { transform: rotate(360deg) translate(42px) rotate(-360deg); }
    }
    html { scroll-behavior: smooth; }
    #top-anchor { position: absolute; top: 0; }
</style>

<div id="top-anchor"></div>
<a href="#top-anchor" id="spaceBtn">
    <div class="orbiting-ship" id="ship1">🚀</div>
    <div class="orbiting-ship" id="ship2">🛸</div>
    <div class="orbiting-ship" id="ship3">✈️</div>
    <div class="center-planet">🌎</div>
</a>
"""
st.markdown(CSS_CODE, unsafe_allow_html=True)

# --- 2. HỆ THỐNG VỆ TINH ---
LIST_KEYS = st.secrets.get("gemini_keys", [])

def safe_ai(prompt):
    if not LIST_KEYS: return "🚨 Cấu hình Secrets lỗi!"
    shuffled = list(LIST_KEYS).copy()
    random.shuffle(shuffled)
    
    # Cấu hình bỏ chặn nội dung chứng khoán
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
    return "🚨 Vệ tinh bận, Kevin thử lại nhé!"

# --- 3. GIAO DIỆN CHÍNH ---
st.sidebar.title("🛡️ KEVIN TV ELITE")
ticker_input = st.sidebar.text_input("Nhập mã (VD: VIC, FPT):", "").upper()
ticker_list = [t.strip() for t in ticker_input.split(",") if t.strip()]

if not ticker_list:
    st.markdown('<div style="text-align:center; padding-top:100px;"><h1>🌌 KEVIN TRADINGVIEW</h1><p>Nhập mã tại Sidebar để bắt đầu.</p></div>', unsafe_allow_html=True)
else:
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
        st.markdown('### 🚀 Phân Tích Kỹ Thuật')
        if st.button("QUÉT TÍN HIỆU AI"):
            df = yf.download(f"{ticker_list[0]}.VN", period="1mo", progress=False)
            if not df.empty:
                last_price = float(df['Close'].iloc[-1])
                st.session_state.anal = safe_ai(f"Mã {ticker_list[0]}, giá {last_price:,.0f}. Phân tích nhanh.")
        st.info(st.session_state.get('anal', "Đang đợi lệnh..."))

    with col_r:
        st.markdown('### 💬 Trợ Lý Trading')
        q = st.chat_input("Hỏi gì đi...")
        if q: st.session_state.chat = safe_ai(f"Mã {ticker_list[0]}: {q}")
        st.info(st.session_state.get('chat', "Sẵn sàng trả lời..."))
