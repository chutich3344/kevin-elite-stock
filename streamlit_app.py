import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import random
import streamlit.components.v1 as components
from vnstock import *

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title='Kevin TV Elite', layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #030406; font-family: 'Inter', sans-serif; }
    .stButton button {
        background: linear-gradient(90deg, #6c3483 0%, #a569bd 100%) !important;
        border: none !important; color: white !important; font-weight: 600 !important;
        border-radius: 12px !important; height: 50px !important; width: 100% !important;
    }
    div[data-testid="stInfo"] {
        background: rgba(13, 17, 23, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important; color: #ccd6f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG VỆ TINH ---
# Lấy danh sách keys và xóa bỏ khoảng trắng thừa nếu có
raw_keys = st.secrets.get("gemini_keys", [])
LIST_KEYS = [k.strip() for k in raw_keys if k.strip()]

def safe_ai(prompt):
    if not LIST_KEYS: return "🚨 Chưa nhận được Key từ Secrets!"
    
    # Thử lần lượt các đời API của Google
    api_versions = ["v1", "v1beta"] 
    
    for k in LIST_KEYS:
        for version in api_versions:
            url = f"https://generativelanguage.googleapis.com/{version}/models/gemini-1.5-flash:generateContent?key={k.strip()}"
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
                if res.status_code == 200:
                    return res.json()['candidates'][0]['content']['parts'][0]['text']
                elif res.status_code == 404:
                    continue # Nếu v1 không thấy thì thử v1beta
                else:
                    return f"🚨 Google báo lỗi {res.status_code}: {res.text[:100]}"
            except Exception as e:
                continue
    return "🚨 Không tìm thấy model phù hợp hoặc lỗi kết nối!"

# --- 3. GIAO DIỆN CHÍNH ---
st.sidebar.title("🛡️ KEVIN TV ELITE")
# Để trống mặc định để người dùng tự nhập
ticker_input = st.sidebar.text_input("Nhập mã chứng khoán (VD: FPT, HPG):", "").upper()

if not ticker_input:
    st.markdown('<div style="text-align:center; padding-top:150px; color:#888;"><h1>🔭 KEVIN STOCK AI</h1><p>Vui lòng nhập mã cổ phiếu ở bên trái để bắt đầu soi lệnh.</p></div>', unsafe_allow_html=True)
else:
    # Biểu đồ TradingView
    tv_html = f"""
    <div style="height:500px;">
      <div id="tv_chart" style="height:500px;"></div>
      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>
      new TradingView.widget({{"autosize": true, "symbol": "HOSE:{ticker_input}", "interval": "D", "theme": "dark", "container_id": "tv_chart"}});
      </script>
    </div>
    """
    components.html(tv_html, height=500)

    st.divider()
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("🚀 Phân Tích AI")
        if st.button(f"QUÉT MÃ {ticker_input}"):
            try:
                # Lấy dữ liệu nhanh qua vnstock
                df = stock_historical_data(symbol=ticker_input, 
                                        start_date="2025-01-01", 
                                        end_date=datetime.now().strftime('%Y-%m-%d'))
                if not df.empty:
                    last_price = df['close'].iloc[-1]
                    st.session_state.anal = safe_ai(f"Mã {ticker_input}, giá {last_price:,.0f}. Phân tích ngắn hạn.")
                else:
                    st.session_state.anal = "❌ Không tìm thấy dữ liệu cho mã này."
            except Exception as e:
                st.session_state.anal = f"❌ Lỗi: {str(e)}"
        st.info(st.session_state.get('anal', "Nhấn nút để quét..."))

    with col_r:
        st.subheader("💬 Trợ Lý")
        q = st.chat_input(f"Hỏi về mã {ticker_input}...")
        if q: 
            st.session_state.chat = safe_ai(f"Mã {ticker_input}: {q}")
        st.info(st.session_state.get('chat', "Sẵn sàng trả lời..."))
