import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
from io import StringIO
import plotly.graph_objects as go

# 1. THIẾT LẬP GIAO DIỆN CHUYÊN NGHIỆP
st.set_page_config(page_title='Kevin Elite Terminal', layout="wide")

# CSS "Ma trận" để làm đẹp bảng và giao diện
st.markdown("""
<style>
    .stApp { background-color: #05070a; color: #e0e0e0; }
    [data-testid="stMetricValue"] { color: #00ff41 !important; font-size: 1.8rem; font-weight: 700; }
    .stDataFrame { border: 1px solid #1e293b; border-radius: 10px; }
    h1, h2, h3 { color: #ffffff; font-family: 'Inter', sans-serif; letter-spacing: -1px; }
    .stButton button {
        background: #1e293b !important; border: 1px solid #334155 !important;
        color: #94a3b8 !important; border-radius: 5px !important;
    }
    .stButton button:hover { border-color: #00ff41 !important; color: #00ff41 !important; }
</style>
""", unsafe_allow_html=True)

# 2. DATA ENGINE
URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBTFokhjgHYmkNhyltxBG6YcULD0vEKbJ9-yiOYKVqXFGJQjlOZMmWZxnoKke6BiS1s3xYAZl959-c/pub?output=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        res = requests.get(URL, timeout=5)
        return pd.read_csv(StringIO(res.text))
    except: return None

df = load_data()

# 3. GIAO DIỆN TERMINAL
st.title("🛰️ KEVIN ELITE TERMINAL v2.0")

if df is not None:
    # HÀNG TRÊN CÙNG: CHỈ SỐ NHANH (METRICS)
    m1, m2, m3, m4 = st.columns(4)
    # Lấy ví dụ giá từ dòng đầu tiên trong Sheets của Kevin
    try:
        price_1 = df.iloc[0, 1] 
        name_1 = df.iloc[0, 0]
        m1.metric(f"{name_1}", f"{price_1:,.0f} đ", "+2.5%")
        m2.metric("VN-INDEX", "1,250.4", "-0.15%")
        m3.metric("THANH KHOẢN", "15.4T", "Tỷ VNĐ")
        m4.metric("TRẠNG THÁI", "📡 ONLINE", "Vệ tinh")
    except: pass

    st.divider()

    # THÂN MÁY: BẢNG GIÁ & CHAT AI
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.subheader("📊 MARKET DATA")
        # Hiển thị bảng kiểu "Dark" xịn xò
        st.dataframe(df, use_container_width=True, height=400)
        
        # Thêm Chart Plotly cho chuyên nghiệp
        fig = go.Figure(go.Scatter(x=df.index, y=df.iloc[:, 1], fill='tozeroy', line_color='#00ff41'))
        fig.update_layout(template='plotly_dark', height=250, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🧠 AI ANALYSIS")
        if "gemini_keys" in st.secrets:
            key = st.secrets["gemini_keys"][0]
            genai.configure(api_key=key)
            
            # Chatbot UI
            container = st.container(height=500, border=True)
            if "messages" not in st.session_state: st.session_state.messages = []

            for m in st.session_state.messages:
                container.chat_message(m["role"]).write(m["content"])

            if p := st.chat_input("Hỏi chuyên gia về danh mục..."):
                st.session_state.messages.append({"role": "user", "content": p})
                container.chat_message("user").write(p)
                
                with st.spinner("Đang tính toán..."):
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    ctx = f"Data: {df.to_string()}. Trả lời ngắn gọn, chuyên nghiệp cho Kevin."
                    ans = model.generate_content(ctx + p).text
                    container.chat_message("assistant").write(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
else:
    st.error("📡 Đang tìm tín hiệu từ Google Sheets...")
