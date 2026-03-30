import streamlit as st
import requests
import json

# --- Cấu hình giao diện ---
st.set_page_config(page_title="Kevin's AI Tester", page_icon="🛰️")
st.title("🛰️ Kevin's AI Tester")
st.write("Dùng để kiểm tra kết nối giữa Streamlit và Google Gemini.")

# --- Lấy và làm sạch Key từ Secrets ---
# App sẽ tìm biến 'gemini_keys' trong phần Secrets của Streamlit
raw_keys = st.secrets.get("gemini_keys", [])

# Nếu Kevin dán dạng list ["key1"] hoặc chỉ 1 chuỗi "key1", code này đều xử lý được
if isinstance(raw_keys, str):
    clean_keys = [raw_keys.strip().replace('"', '').replace("'", "")]
else:
    clean_keys = [k.strip().replace('"', '').replace("'", "") for k in raw_keys if k.strip()]

# --- Giao diện Test ---
if not clean_keys:
    st.error("🚨 Lỗi: Chưa tìm thấy Key nào trong Secrets! Kevin hãy kiểm tra lại mục 'gemini_keys'.")
else:
    key_to_test = clean_keys[0]
    st.info(f"Đang chuẩn bị test với Key đuôi: `...{key_to_test[-4:]}`")

    if st.button("🚀 BẤM ĐỂ TEST KẾT NỐI VỆ TINH"):
        with st.spinner("Đang gửi tín hiệu lên Google..."):
            # URL gọi Model Gemini 1.5 Flash
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key_to_test}"
            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [{"parts": [{"text": "Hello Gemini, this is Kevin. Are you active?"}]}]
            }

            try:
                res = requests.post(url, json=payload, headers=headers, timeout=15)
                
                if res.status_code == 200:
                    st.success("✅ VỆ TINH ĐÃ KẾT NỐI THÀNH CÔNG!")
                    data = res.json()
                    # Hiển thị câu trả lời từ AI
                    ai_response = data['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(f"**Gemini trả lời:** {ai_response}")
                else:
                    st.error(f"❌ THẤT BẠI: Google trả về lỗi {res.status_code}")
                    # Hiện nguyên cục JSON lỗi để Kevin chụp màn hình gửi mình soi
                    st.json(res.json())
                    
                    # Giải mã nhanh một số lỗi phổ biến
                    if res.status_code == 400:
                        st.warning("👉 Lỗi 400: Thường là do Key bị sai ký tự hoặc dán sai định dạng.")
                    elif res.status_code == 403:
                        st.warning("👉 Lỗi 403: Key chưa được bật API hoặc quốc gia của bạn bị chặn.")
            
            except Exception as e:
                st.error(f"🚨 Lỗi kết nối vật lý: {str(e)}")
                st.write("Kiểm tra lại mạng hoặc server Streamlit.")

st.divider()
st.caption("Admin hỗ trợ Kevin - 2026")
