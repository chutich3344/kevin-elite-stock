import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
from io import StringIO
import plotly.graph_objects as go

# --- 1. CONFIG GIAO DIỆN TERMINAL ---
st.set_page_config(page_title='Kevin Elite Terminal', layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #030406; color: #e0e0e0; }
    .stDataFrame { border: 1px solid #1db954 !important; border-radius: 5px; }
    [data-testid="stMetricValue"] { 
        color: #1db954 !important; 
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 10px rgba(29, 185, 84, 0.5);
    }
    .header-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #1db954, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBTFokhjgHYmkNhyltxBG6YcULD0vEKbJ9-yiOYKVqXFGJQjlOZMmWZxnoKke6BiS1s3xYAZl959-c/pub?output=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        return pd.read_csv(StringIO(res.text))
    except: return None

# --- 3. AI CHUYÊN GIA (SỬA LỖI 404) ---
def get_ai_response(prompt, data):
    try:
        raw_keys = st.secrets.get("gemini_keys", [])
        if not raw_keys: return "🚨 Thiếu API Key!"
        
        api_key = raw_keys[0].strip().replace('"', '')
        genai.configure(api_key=api_key)
        
        # SỬA LỖI 404: Gọi model theo đúng path chuẩn 2026
        # Dùng 'models/gemini-1.5-flash' hoặc 'gemini-1.5-flash' tùy phiên bản SDK
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        ctx = f"Bạn là chuyên gia tài chính của Kevin. Dữ liệu: {data}. Trả lời cực ngắn, Pro."
        # Đảm bảo không dùng v1beta nếu SDK đã tự nhận diện v1
        response = model.generate_content(ctx + "\n\n" + prompt)
        return response.text
    except Exception as e:
        return f"🚨 Lỗi kết nối AI: {str(e)}"

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown("<h1 class='header-text'>KEVIN ELITE TERMINAL v3.1</h1>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # Top Bar Metrics
    cols = st.columns(len(df.head(4)))
    for i, col in enumerate(cols):
        try:
            ticker, price = df.iloc[i, 0], df.iloc[i, 1]
            col.metric(label=f"● {ticker}", value=f"{price:,.0f}")
        except: pass

    st.divider()

    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.subheader("📊 MARKET DATA")
        # FIX CẢNH BÁO: Đổi use_container_width sang width='stretch'
        st.dataframe(df, width='stretch', height=350)
        
        fig = go.Figure(go.Scatter(x=df.index, y=df.iloc[:, 1], fill='tozeroy', line_color='#1db954'))
        fig.update_layout(template='plotly_dark', height=250, margin=dict(l=0,r=0,t=0,b=0),
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        # FIX CẢNH BÁO cho Plotly
        st.plotly_chart(fig, width='stretch')

    with c2:
        st.subheader("💬 AI ASSISTANT")
        if "messages" not in st.session_state: st.session_state.messages = []
        
        chat_box = st.container(height=450)
        for m in st.session_state.messages:
            chat_box.chat_message(m["role"]).write(m["content"])

        if p := st.chat_input("Soi mã FPT, VIC..."):
            st.session_state.messages.append({"role": "user", "content": p})
            chat_box.chat_message("user").write(p)
            
            with st.spinner("AI đang soi lệnh..."):
                ans = get_ai_response(p, df.to_string())
                chat_box.chat_message("assistant").write(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
else:
    st.warning("📡 Đang kết nối vệ tinh...")
