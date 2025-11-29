import streamlit as st
import pandas as pd
import os
import io

def process_file_uploaded(uploaded_file):
    """Đọc UploadedFile thành DataFrame của Pandas."""
    if uploaded_file is None:
        return None

    # Kiểm tra loại tệp và đọc
    if uploaded_file.name.endswith('.csv'):
        # Đọc CSV
        return pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
    elif uploaded_file.name.endswith(('.xlsx', '.xls')):
        # Đọc Excel (dùng BytesIO vì là tệp nhị phân)
        return pd.read_excel(io.BytesIO(uploaded_file.getvalue()))
    else:
        st.error("Định dạng tệp không được hỗ trợ. Vui lòng chọn CSV hoặc XLSX.")
        return None