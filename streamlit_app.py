import streamlit as st
import pandas as pd
import google.generativeai as genai
import requests
from io import StringIO

# 1. CẤU HÌNH VỆ TINH
st.set_page_config(page_title='Kevin Elite AI', layout="wide", page_icon="🛰️")

# LINK CSV CHUẨN CỦA KEVIN
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBTFokhjgHYmkNhyltxBG6YcULD0vEKbJ9-yiOYKVqXFGJQjlOZMmWZxnoKke6BiS1s3xYAZl959-c/pub?output=csv"

# 2. HÀM ĐỌC DỮ LIỆU TỪ GOOGLE SHEETS (ĐÃ GIA CỐ)
@st.cache_data(ttl=60) # Cập nhật dữ liệu mới mỗi 60 giây
def load_data_from_sheets(url):
    try:
        # Thêm Header giả lập trình duyệt để Google không chặn Server
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Đọc nội dung text trả về và chuyển thành DataFrame
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            return df
        else:
            st.error(f"🚨 Google trả về lỗi: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"🚨 Lỗi kết nối vật lý: {e}")
        return None

# 3. THIẾT LẬP GEMINI CHUYÊN GIA TÀI CHÍNH
def get_gemini_response(user_input, stock_data):
    raw_keys = st.secrets.get("gemini_keys", [])
    if not raw_keys: return "🚨 Thiếu Key Gemini trong phần Secrets!"
    
    key = raw_keys[0].strip().replace('"', '').replace("'", "")
    genai.configure(api_key=key)
    
    instruction = f"""
    Bạn là Kevin Elite AI - Chuyên gia tài chính số 1. 
    Dữ liệu từ Google Sheets của Kevin hiện tại là:
    {stock_data}
    Nhiệm vụ: Phân tích các mã này, tư vấn điểm mua/bán và trả lời mọi thắc mắc về tài chính. 
    Nếu dữ liệu trống, hãy báo Kevin nhập mã vào Sheets.
    """
    
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction)
    response = model.generate_content(user_input)
    return response.text

# 4. GIAO DIỆN CHÍNH
st.title("🛰️ KEVIN ELITE FINANCE BOT")

# Thực hiện load dữ liệu
df = load_data_from_sheets(SHEET_CSV_URL)

if df is not None:
    data_string = df.to_string()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Bảng giá từ Sheets")
        st.dataframe(df, use_container_width=True)
        if st.button("🔄 Làm mới dữ liệu"):
            st.cache_data.clear()
            st.rerun()
        
    with col2:
        st.subheader("💬 Chat với Chuyên gia Gemini")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Hỏi về cổ phiếu của bạn..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Gemini đang soi kèo..."):
                    response = get_gemini_response(prompt, data_string)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("⚠️ Đang chờ kết nối với Google Sheets... Kevin hãy kiểm tra link CSV hoặc nhấn nút làm mới nhé!")
