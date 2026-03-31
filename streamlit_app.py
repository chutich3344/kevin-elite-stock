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
    /* Tổng thể Dark Mode sâu */
    .stApp { background-color: #030406; color: #e0e0e0; }
    
    /* Làm đẹp bảng giá giống bảng điện */
    .stDataFrame { 
        border: 1px solid #1db954 !important; 
        border-radius: 5px;
    }
    
    /* Chỉ số Metric kiểu Neon */
    [data-testid="stMetricValue"] { 
        color: #1db954 !important; 
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 10px rgba(29, 185, 84, 0.5);
    }
    
    /* Thanh cuộn và Chat input */
    .stChatInputContainer { bottom: 20px !important; }
    
    /* Header chuyên nghiệp */
    .header-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #1db954, #191414);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (Google Sheets) ---
URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBTFokhjgHYmkNhyltxBG6YcULD0vEKbJ9-yiOYKVqXFGJQjlOZMmWZxnoKke6BiS1s3xYAZl959-c/pub?output=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(URL, headers=headers, timeout=5)
        return pd.read_csv(StringIO(res.text))
    except: return None

# --- 3. AI CHUYÊN GIA (Sửa lỗi 404) ---
def get_ai_response(prompt, data):
    try:
        raw_keys = st.secrets.get("gemini_keys", [])
        if not raw_keys: return "🚨 Thiếu API Key!"
        
        api_key = raw_keys[0].strip().replace('"', '')
        genai.configure(api_key=api_key)
        
        # SỬA LỖI 404: Dùng cấu hình model chuẩn
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", # Đảm bảo đúng tên model
        )
        
        ctx = f"Bạn là chuyên gia tài chính của Kevin. Dữ liệu hiện tại: {data}. Hãy phân tích cực ngắn gọn, phong cách chuyên nghiệp."
        response = model.generate_content(ctx + "\n\nCâu hỏi: " + prompt)
        return response.text
    except Exception as e:
        return f"🚨 Lỗi AI: {str(e)}"

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown("<h1 class='header-text'>KEVIN ELITE TERMINAL v3.0</h1>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # Top Bar Metrics
    cols = st.columns(len(df.head(4)))
    for i, col in enumerate(cols):
        try:
            ticker = df.iloc[i, 0]
            price = df.iloc[i, 1]
            col.metric(label=f"● {ticker}", value=f"{price:,.0f}")
        except: pass

    st.divider()

    # Main Dashboard
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.subheader("📊 DÒNG TIỀN THỊ TRƯỜNG")
        st.dataframe(df, use_container_width=True, height=350)
        
        # Biểu đồ Area Chart màu xanh lá
        fig = go.Figure(go.Scatter(x=df.index, y=df.iloc[:, 1], fill='tozeroy', line_color='#1db954'))
        fig.update_layout(
            template='plotly_dark', height=250, 
            margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("💬 AI TRADING ASSISTANT")
        # Chat container
        if "messages" not in st.session_state: st.session_state.messages = []
        
        chat_box = st.container(height=450)
        for m in st.session_state.messages:
            chat_box.chat_message(m["role"]).write(m["content"])

        if p := st.chat_input("Hỏi chuyên gia về mã FPT, VIC..."):
            st.session_state.messages.append({"role": "user", "content": p})
            chat_box.chat_message("user").write(p)
            
            with st.spinner("AI đang soi lệnh..."):
                ans = get_ai_response(p, df.to_string())
                chat_box.chat_message("assistant").write(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
else:
    st.warning("📡 Đang kết nối vệ tinh...")
