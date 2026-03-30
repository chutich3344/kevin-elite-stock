import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import random
import time
import streamlit.components.v1 as components
from vnstock import *

# --- 1. CẤU HÌNH & CSS (OCD APPROVED) ---
st.set_page_config(page_title='Kevin TV Elite', layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #030406; font-family: 'Inter', sans-serif; }
    .stButton button {
        background: linear-gradient(90deg, #6c3483 0%, #a569bd 100%) !important;
        border: none !important; color: white !important; font-weight: 600 !important;
        height: 52px !important; border-radius: 12px !important; width: 100% !important;
    }
    div[data-testid="stInfo"] {
        background: rgba(13, 17, 23, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important; padding: 25px !important;
        color: #ccd6f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG VỆ TINH GEMINI ---
LIST_KEYS = st.secrets.get("gemini_keys", [])

def safe_ai(prompt):
    if not LIST_KEYS: return "🚨 Cấu hình Secrets lỗi!"
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
            else:
                print(f"Lỗi Key: {res.status_code}")
        except: continue
    return "🚨 Vệ tinh bận (Lỗi kết nối Google), Kevin thử lại nhé!"

# --- 3. GIAO DIỆN CHÍNH ---
st.sidebar.title("🛡️ KEVIN TV ELITE")
ticker_input = st.sidebar.text_input("Nhập mã (VD: VIC, FPT):", "VIC").upper()
ticker_list = [t.strip() for t in ticker_input.split(",") if t.strip()]

if not ticker_list:
    st.info("Nhập mã tại Sidebar để bắt đầu.")
else:
    tabs = st.tabs([f"📊 {t}" for t in ticker_list])
    for i, ticker in enumerate(ticker_list):
        with tabs[i]:
            tv_html = f"""
            <div style="height:550px;">
              <div id="tv_{ticker}" style="height:550px;"></div>
              <script src="https://s3.tradingview.com/tv.js"></script>
              <script>
              new TradingView.widget({{"autosize": true, "symbol": "HOSE:{ticker}", "theme": "dark", "container_id": "tv_{ticker}"}});
              </script>
            </div>
            """
            components.html(tv_html, height=550)

    st.divider()
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown('### 🚀 Phân Tích Kỹ Thuật')
        if st.button("QUÉT TÍN HIỆU AI"):
            with st.spinner('Đang lấy dữ liệu thị trường VN...'):
                try:
                    # Dùng vnstock để lấy dữ liệu thay vì yfinance
                    df = stock_historical_data(symbol=ticker_list[0], 
                                            start_date="2024-01-01", 
                                            end_date=datetime.now().strftime('%Y-%m-%d'), 
                                            resolution='1D', type='stock')
                    if not df.empty:
                        last_price = df['close'].iloc[-1]
                        prompt = f"Mã {ticker_list[0]}, giá hiện tại là {last_price:,.0f} VNĐ. Phân tích xu hướng kỹ thuật ngắn hạn dựa trên mức giá này."
                        st.session_state.anal = safe_ai(prompt)
                    else:
                        st.session_state.anal = "❌ Dữ liệu trống. Hãy kiểm tra lại mã niêm yết."
                except Exception as e:
                    st.session_state.anal = f"❌ Lỗi vnstock: {str(e)}"
        
        st.info(st.session_state.get('anal', "Đang đợi lệnh..."))

    with col_r:
        st.markdown('### 💬 Trợ Lý Trading')
        q = st.chat_input("Hỏi gì về mã này...")
        if q: 
            st.session_state.chat = safe_ai(f"Mã {ticker_list[0]}: {q}")
        st.info(st.session_state.get('chat', "Sẵn sàng trả lời..."))
