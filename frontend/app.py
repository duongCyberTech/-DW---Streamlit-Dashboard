import streamlit as st

st.title("Trang chủ")

st.write("Chọn module bạn muốn làm việc:")

# Link đến file trong thư mục pages hoặc file được định nghĩa trong st.navigation
st.page_link("pages/dashboard.py", label="Dashboard", icon="💰")
st.page_link("pages/dss_page.py", label="Mall Profit Optimization", icon="🛡️", help="Chỉ dành cho quản lý")