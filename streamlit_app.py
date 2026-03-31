import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(page_title="Kevin Elite", page_icon="🛰️")

# LINK CSV CHUẨN (Đảm bảo đuôi ?output=csv)
URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBTFokhjgHYmkNhyltxBG6YcULD0vEKbJ9-yiOYKVqXFGJQjlOZMmWZxnoKke6BiS1s3xYAZl959-c/pub?output=csv"

st.title("🛰️ KEVIN ELITE MONITOR")

# Hàm lấy dữ liệu có giới hạn thời gian (Timeout)
def fetch_fast():
    try:
        # Nếu sau 7 giây không phản hồi, tự ngắt để tránh Loading hoài
        res = requests.get(URL, timeout=7)
        if res.status_code == 200:
            return pd.read_csv(StringIO(res.text))
    except:
        return None
    return None

# Kiểm tra dữ liệu
df = fetch_fast()

if df is not None:
    st.success("✅ Đã kết nối!")
    st.dataframe(df)
else:
    st.error("⚠️ Sóng yếu! Google Sheets chưa phản hồi. Kevin hãy kiểm tra lại link hoặc nhấn nút bên dưới.")
    if st.button("🔄 THỬ KẾT NỐI LẠI"):
        st.rerun()
