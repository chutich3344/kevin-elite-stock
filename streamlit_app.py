import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
from io import StringIO

# 1. CẤU HÌNH
st.set_page_config(page_title='Kevin Elite AI', layout="wide")

# DÁN LINK MỚI (CÓ ĐUÔI output=csv) VÀO ĐÂY
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBTFokhjgHYmkNhyltxBG6YcULD0vEKbJ9-yiOYKVqXFGJQjlOZMmWZxnoKke6BiS1s3xYAZl959-c/pub?output=csv"

# 2. HÀM ĐỌC DATA (CHỐNG TREO)
@st.cache_data(ttl=10) # Chỉ lưu cache 10 giây để update giá nhanh
def load_data():
    try:
        # Giả lập trình duyệt để lấy file CSV cực nhanh
        res = requests.get(SHEET_URL, timeout=5)
        if res.status_code == 200:
            return pd.read_csv(StringIO(res.text))
    except:
        return None
    return None

# 3. AI CHUYÊN GIA TÀI CHÍNH
def ask_gemini(msg, data):
    key = st.secrets["gemini_keys"][0].strip().replace('"', '')
    genai.configure(api_key=key)
    # Dạy Gemini làm chuyên gia chứng khoán
    role = f"Bạn là chuyên gia chứng khoán của Kevin. Dữ liệu: {data}. Chỉ trả lời về tài chính."
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=role)
    return model.generate_content(msg).text

# 4. GIAO DIỆN
st.title("🛰️ KEVIN ELITE FINANCE BOT")

df = load_data()

if df is not None:
    st.success("✅ Đã thông suốt!")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Bảng giá")
        st.write(df) # Hiện bảng giá từ Sheets
        
    with col2:
        st.subheader("💬 Chat chuyên gia")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Hiển thị chat
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["txt"])

        if p := st.chat_input("Hỏi AI về mã trong Sheets..."):
            st.session_state.chat_history.append({"role": "user", "txt": p})
            with st.chat_message("user"): st.markdown(p)
            
            with st.chat_message("assistant"):
                ans = ask_gemini(p, df.to_string())
                st.markdown(ans)
                st.session_state.chat_history.append({"role": "assistant", "txt": ans})
else:
    st.error("⚠️ Vẫn đang Loading? Kevin hãy chọn định dạng .CSV trong Google Sheets nhé!")
    if st.button("🔄 THỬ LẠI"): st.rerun()
