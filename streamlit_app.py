import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import random
from vnstock3 import Vnstock # Chuẩn V3

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
raw_keys = st.secrets.get("gemini_keys", [])
LIST_KEYS = [k.strip().replace('"', '').replace("'", "") for k in raw_keys if k.strip()]

def safe_ai(prompt):
    if not LIST_KEYS: return "🚨 Kiểm tra lại Secrets (gemini_keys)!"
    shuffled = list(LIST_KEYS).copy()
    random.shuffle(shuffled)
    for k in shuffled:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={k}"
        try:
            res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
        except: continue
    return "🚨 Vệ tinh bận, thử lại sau nhé Kevin!"

# --- 3. GIAO DIỆN CHÍNH ---
st.sidebar.title("🛡️ KEVIN TV ELITE")
ticker = st.sidebar.text_input("Nhập mã (VD: FPT, VIC):", "FPT").upper()

if ticker:
    import streamlit.components.v1 as components
    tv_html = f"""
    <div style="height:500px;">
      <div id="tv_chart" style="height:500px;"></div>
      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>
      new TradingView.widget({{"autosize": true, "symbol": "HOSE:{ticker}", "interval": "D", "theme": "dark", "container_id": "tv_chart"}});
      </script>
    </div>
    """
    components.html(tv_html, height=500)

    st.divider()
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("🚀 Phân Tích AI")
        if st.button(f"QUÉT MÃ {ticker}"):
            try:
                # FIX DÒNG NÀY: Dùng Vnstock V3 đúng cách
                stock = Vnstock().stock(symbol=ticker, source='VCI')
                df = stock.quote.history(start='2025-01-01', end=datetime.now().strftime('%Y-%m-%d'))
                
                if not df.empty:
                    last_price = df['close'].iloc[-1]
                    st.session_state.anal = safe_ai(f"Mã {ticker}, giá hiện tại {last_price:,.0f}đ. Phân tích kỹ thuật ngắn hạn.")
                else:
                    st.session_state.anal = "❌ Dữ liệu trống, check lại mã nhé."
            except Exception as e:
                st.session_state.anal = f"❌ Lỗi: {str(e)}"
        st.info(st.session_state.get('anal', "Đang chờ lệnh..."))

    with col_r:
        st.subheader("💬 Trợ Lý")
        q = st.chat_input("Hỏi gì đi...")
        if q: st.session_state.chat = safe_ai(f"Mã {ticker}: {q}")
        st.info(st.session_state.get('chat', "Sẵn sàng..."))
