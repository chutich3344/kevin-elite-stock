import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import random
import streamlit.components.v1 as components
from vnstock3 import Vnstock

# --- 1. CONFIG GIAO DIỆN ---
st.set_page_config(page_title='Kevin TV Elite', layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #030406; font-family: 'Inter', sans-serif; }
    .stButton button {
        background: linear-gradient(90deg, #6c3483 0%, #a569bd 100%) !important;
        border: none !important; color: white !important; font-weight: 600 !important;
        border-radius: 12px !important; height: 50px !important;
    }
    div[data-testid="stInfo"] {
        background: rgba(13, 17, 23, 0.9) !important;
        border-radius: 15px !important; color: #ccd6f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HỆ THỐNG AI (DÙNG KEY ĐÃ TEST NGON) ---
raw_keys = st.secrets.get("gemini_keys", [])
LIST_KEYS = [k.strip().replace('"', '').replace("'", "") for k in raw_keys if k.strip()]

def safe_ai(prompt):
    if not LIST_KEYS: return "🚨 Lỗi: Check Secrets gemini_keys!"
    # Dùng đúng cơ chế Kevin vừa test thành công
    k = LIST_KEYS[0]
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={k}"
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
    except: pass
    return "🚨 Vệ tinh bận, nhấn Quét lại nhé Kevin!"

# --- 3. APP CHÍNH ---
st.sidebar.title("🛡️ KEVIN TV ELITE")
ticker = st.sidebar.text_input("Nhập mã (VD: FPT, HPG, VIC):", "").upper()

if not ticker:
    st.markdown('<div style="text-align:center; padding-top:150px; color:#888;"><h1>🔭 KEVIN ELITE STOCK</h1><p>Nhập mã tại Sidebar để bắt đầu soi lệnh.</p></div>', unsafe_allow_html=True)
else:
    # Biểu đồ TradingView
    tv_html = f"""
    <div style="height:500px;"><div id="tv_chart" style="height:500px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>new TradingView.widget({{"autosize": true, "symbol": "HOSE:{ticker}", "interval": "D", "theme": "dark", "container_id": "tv_chart"}});</script>
    </div>
    """
    components.html(tv_html, height=500)

    st.divider()
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("🚀 Phân Tích AI")
        if st.button(f"QUÉT MÃ {ticker}"):
            with st.spinner('Đang lách rào lấy dữ liệu...'):
                df = pd.DataFrame()
                # Thử các nguồn SSI/VCI/DNSE (Bỏ qua TCBS đang lỗi)
                for src in ['SSI', 'VCI', 'DNSE']:
                    try:
                        stock = Vnstock().stock(symbol=ticker, source=src)
                        df = stock.quote.history(start='2025-01-01', end=datetime.now().strftime('%Y-%m-%d'))
                        if df is not None and not df.empty: break
                    except: continue
                
                if not df.empty:
                    lp = df['close'].iloc[-1]
                    st.session_state.anal = safe_ai(f"Mã {ticker}, giá {lp:,.0f}đ. Phân tích kỹ thuật ngắn hạn.")
                else:
                    st.session_state.anal = "❌ Lỗi 403: Các nguồn dữ liệu đang chặn IP server. Thử lại sau nhé!"
        st.info(st.session_state.get('anal', "Nhấn nút để bắt đầu..."))

    with col_r:
        st.subheader("💬 Trợ Lý Trading")
        q = st.chat_input(f"Hỏi Gemini về {ticker}...")
        if q: 
            st.session_state.chat = safe_ai(f"Mã {ticker}: {q}")
        
        st.info(st.session_state.get('chat', "Sẵn sàng trả lời..."))
        
        if st.button("🗑️ XOÁ LỊCH SỬ"):
            for k in ['chat', 'anal']:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
