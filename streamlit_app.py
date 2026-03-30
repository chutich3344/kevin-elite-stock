import streamlit as st
import time

# --- Thêm hàm hiển thị thông báo kiểu "Elite" ---
def show_status(message, type="info"):
    if type == "error":
        st.toast(message, icon="🚨")
    elif type == "success":
        st.toast(message, icon="✅")
    else:
        st.toast(message, icon="🛰️")

# --- Logic kiểm tra thời gian giữa 2 lần nhấn ---
if 'last_request' not in st.session_state:
    st.session_state.last_request = 0

current_time = time.time()
wait_time = 30  # Giãn cách 30 giây để né Rate Limit

if st.button(f"🔍 PHÂN TÍCH {ticker}"):
    elapsed = current_time - st.session_state.last_request
    
    if elapsed < wait_time:
        remaining = int(wait_time - elapsed)
        # Thông báo kiểu Toast cực xịn ở góc màn hình
        show_status(f"Kevin ơi, chờ {remaining}s nữa để 'né' Google quét nhé!", type="info")
    else:
        st.session_state.last_request = current_time
        # Chạy hàm lấy dữ liệu của bạn ở đây...
        with st.spinner("Đang soi lệnh..."):
            # Code lấy data cũ của mình
            pass
