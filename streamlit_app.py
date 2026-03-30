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

    /* Button & Input */
    .stButton button {
        background: linear-gradient(90deg, #6c3483 0%, #a569bd 100%) !important;
        border: none !important; color: white !important; font-weight: 600 !important;
        height: 52px !important; border-radius: 12px !important; width: 100% !important;
        transition: 0.3s ease;
    }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(165, 105, 189, 0.4); }

    /* Khung Info AI */
    div[data-testid="stInfo"] {
        background: rgba(13, 17, 23, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important; padding: 25px !important;
        min-height: 350px !important; color: #ccd6f6 !important;
    }

    /* 🔥 NÚT VŨ TRỤ TO TOP 🌎🛸 🔥 */
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
    @keyframes thrustGlow {
        0%, 100% { box-shadow: 0 0 10px rgba(165, 105, 189, 0.2); }
        50% { box-shadow: 0 0 30px rgba(165, 105, 189, 0.8); }
    }
    .deep-space-thrusting { animation: thrustGlow 0.5s infinite !important; border-color: #a569bd !important; }
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

<script>
    const spaceBtn = document.getElementById('spaceBtn');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 200) { spaceBtn.classList.add('deep-space-thrusting'); }
        else { spaceBtn.classList.remove('deep-space-thrusting'); }
    });
</script>
"""
st.markdown(CSS_CODE, unsafe_allow_html=True)

# --- 2. HỆ THỐNG VỆ TINH (SECRETS BASED) ---
LIST_KEYS = st.secrets.get("gemini_keys", [])
# Đoạn này để debug - Kevin dán vào dưới dòng LIST_KEYS
st.sidebar.write(f"🔍 Đang quét hệ thống...")
st.sidebar.write(f"✅ Đã nhận {len(LIST_KEYS)} Keys.")

if len(LIST_KEYS) > 0:
    # Hiện 4 ký tự cuối của từng key để bạn đối chiếu xem có đúng key mới chưa
    for i, k in enumerate(LIST_KEYS):
        st.sidebar.text(f"Vệ tinh {i+1}: ...{k[-4:]}")
else:
    st.sidebar.error("❌ CHƯA ĐỌC ĐƯỢC KEY NÀO!")

def safe_ai(prompt):
    # Cấu hình nới lỏng an toàn để tránh bị chặn nhầm nội dung chứng khoán
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    shuffled = list(LIST_KEYS).copy()
    random.shuffle(shuffled)
    
    for k in shuffled:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={k}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "safetySettings": safety_settings # Thêm dòng này
        }
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            elif res.status_code == 429:
                time.sleep(1) # Nghỉ 1s rồi đổi project
                continue
        except:
            continue
    return "🚨 Vệ tinh vẫn kẹt tại trạm mặt đất VN. Kevin thử bật VPN hoặc deploy Cloud nhé!"

# --- 3. SIDEBAR & TRADINGVIEW ---
st.sidebar.title("🛡️ KEVIN TV ELITE")
ticker_input = st.sidebar.text_input("Nhập mã (VD: VIC, FPT, VNM):", "").upper()
ticker_list = [t.strip() for t in ticker_input.split(",") if t.strip()]

if not ticker_list:
    st.markdown('<div style="text-align:center; padding:150px;"><h1>🌌 KEVIN TRADINGVIEW</h1><p>Hệ thống sẵn sàng. Nhập mã tại Sidebar để kích hoạt vệ tinh.</p></div>', unsafe_allow_html=True)
else:
    tabs = st.tabs([f"📊 {t}" for t in ticker_list])
    for i, ticker in enumerate(ticker_list):
        with tabs[i]:
            tv_symbol = f"HOSE:{ticker}"
            tv_html = f"""
            <div class="tradingview-widget-container" style="height:550px;">
              <div id="tradingview_{ticker}" style="height:calc(100% - 32px);"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget({{
                "autosize": true, "symbol": "{tv_symbol}", "interval": "D",
                "timezone": "Asia/Ho_Chi_Minh", "theme": "dark", "style": "1",
                "locale": "vi_VN", "toolbar_bg": "#f1f3f6", "enable_publishing": false,
                "hide_side_toolbar": false, "allow_symbol_change": true,
                "container_id": "tradingview_{ticker}"
              }});
              </script>
            </div>
            """
            components.html(tv_html, height=550)

# --- 4. CÂN BẰNG PHÂN TÍCH ---
if ticker_list:
    st.divider()
    col_l, col_r = st.columns(2, gap="large")
    current_ticker = ticker_list[0] 

    with col_l:
        st.markdown('<div class="tier-title">🚀 Phân Tích Kỹ Thuật</div>', unsafe_allow_html=True)
        if st.button("QUÉT TÍN HIỆU AI"):
            with st.spinner('Đang tải dữ liệu yFinance...'):
                try:
                    df = yf.download(f"{current_ticker}.VN", period="1mo", progress=False)
                    if not df.empty:
                        # FIX LỖI TYPEERROR: Ép kiểu float cho giá đóng cửa cuối cùng
                        last_price = float(df['Close'].iloc[-1])
                        st.session_state.anal = safe_ai(f"Mã {current_ticker}: Giá hiện tại {last_price:,.0f} VNĐ. Phân tích kỹ thuật ngắn gọn điểm Mua/Bán.")
                    else:
                        st.session_state.anal = f"❌ Không tìm thấy dữ liệu cho {current_ticker}"
                except Exception as e:
                    st.session_state.anal = f"🚨 Lỗi: {str(e)}"
        
        st.info(st.session_state.get('anal', "🎯 Hệ thống đang đợi lệnh quét từ Kevin..."))

    with col_r:
        st.markdown('<div class="tier-title">💬 Trợ Lý Trading</div>', unsafe_allow_html=True)
        q = st.chat_input("Hỏi AI về chiến lược của mã này...")
        if q:
            with st.spinner('Vệ tinh đang trả lời...'):
                ans = safe_ai(f"Mã {current_ticker}: {q}")
                st.session_state.last_chat = ans
        
        st.info(st.session_state.get('last_chat', "🤝 Tôi có thể giúp gì cho bạn về mã này?"))

# Hiển thị số lượng vệ tinh đang hoạt động ở cuối sidebar
st.sidebar.markdown(f"--- \n📡 **Vệ tinh online:** {len(LIST_KEYS)} Projects")
