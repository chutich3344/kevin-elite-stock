import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai

# 1. CẤU HÌNH VỆ TINH
st.set_page_config(page_title='Kevin Elite AI', layout="wide")

# DÁN CÁI LINK CSV BẠN VỪA COPY Ở BƯỚC 1 VÀO ĐÂY
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBTFokhjgHYmkNhyltxBG6YcULD0vEKbJ9-yiOYKVqXFGJQjlOZMmWZxnoKke6BiS1s3xYAZl959-c/pubhtml"

# 2. THIẾT LẬP GEMINI CHUYÊN GIA TÀI CHÍNH
def get_gemini_response(user_input, stock_data):
    raw_keys = st.secrets.get("gemini_keys", [])
    if not raw_keys: return "🚨 Thiếu Key Gemini!"
    
    key = raw_keys[0].strip().replace('"', '').replace("'", "")
    genai.configure(api_key=key)
    
    # Chỉ dẫn hệ thống để Gemini biến thành chuyên gia chứng khoán
    instruction = f"""
    Bạn là Kevin Elite AI - Chuyên gia tài chính. 
    Dữ liệu thị trường hiện tại từ Google Sheets của Kevin: {stock_data}.
    Hãy trả lời dựa trên số liệu này. Nếu người dùng hỏi ngoài lề, hãy nhắc họ tập trung vào chứng khoán.
    """
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction)
    
    response = model.generate_content(user_input)
    return response.text

# 3. GIAO DIỆN APP
st.title("🛰️ KEVIN ELITE FINANCE BOT")

# Tự động đọc dữ liệu từ Sheets
try:
    df = pd.read_csv(SHEET_CSV_URL)
    data_string = df.to_string() # Chuyển bảng thành chữ cho AI đọc
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Dữ liệu từ Sheets")
        st.dataframe(df, use_container_width=True)
        
    with col2:
        st.subheader("💬 Chat với Chuyên gia Gemini")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Hiển thị lịch sử chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Hỏi về mã cổ phiếu trong Sheets của bạn..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = get_gemini_response(prompt, data_string)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

except Exception as e:
    st.error("Chưa kết nối được với Google Sheets. Kevin kiểm tra lại link CSV nhé!")
