import streamlit as st
import pandas as pd
import plotly.express as px
import api_call.cache as ca
import os
import utils.uploader as uu

# --- CONFIG ---

st.set_page_config(page_title="Business Dashboard", layout="wide")
st.markdown("<h1 style='text-align:center;'>📈 Business Overview Dashboard</h1>", unsafe_allow_html=True)
st.write("")

tab1, tab2, tab3 = st.tabs(['Overall', 'RFM Analysis', 'Prediction'])

with tab1:
    # --- API CALL ---
    transactions = ca.get_all_transactions()
    stats = ca.stats_counting()

    # --- LOAD CSS ---
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # --- LOAD DATA ---
    df = pd.read_csv("data/sample_data.csv")

    st.write("## **Tổng quan dữ liệu**")
    # --- METRIC CARDS ---
    col1, col2, col3 = st.columns(3)

    total_revenue = df["revenue"].sum()
    total_orders = df["orders"].sum()
    total_customers = df["customers"].iloc[-1]

    with col1:
        st.markdown(f"<div class='data-card'><div class='metric-value'>${stats['total_revenue']:,}</div><div class='metric-label'>Tổng doanh thu</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='data-card'><div class='metric-value'>{stats['total_records']:,}</div><div class='metric-label'>Tổng số giao dịch</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='data-card'><div class='metric-value'>${stats['avg_price']:,}</div><div class='metric-label'>Mức chi tiêu trung bình</div></div>", unsafe_allow_html=True)

    st.write("---")

    # Revenue line chart
    col1, col2 = st.columns(2)
    with col1:
        selected_period = st.selectbox("Period: ", ['monthly', '7-days', 'quarter', 'annually'])
    with col2:
        if selected_period == 'monthly':
            selected_value = st.selectbox("Year: ", stats['years'])
        elif selected_period == 'quarter' or selected_period == 'annually':
            selected_value = st.selectbox("N Lastest Year: ", range(1, len(stats['years']) + 1))
        else: selected_value = 1
    time_revenue = ca.revenue_in_year_by_month(selected_value, selected_period)
    df_time_revenue = pd.DataFrame(time_revenue['revenue_by_time'])

    df_cat_revenue = pd.DataFrame(time_revenue['revenue_cat'])
    st.write(df_time_revenue)

    # --- CHARTS ---
    col1, col2 = st.columns(2)
    with col1:
        all_malls = df_time_revenue['mall'].unique().tolist()
        selected_malls = st.multiselect(
            "Chọn Mall để hiển thị:",
            options=all_malls,
            default=all_malls[:3] # Mặc định hiện Top 5
        )
        filtered_df = df_time_revenue[df_time_revenue['mall'].isin(selected_malls)]
        filtered_df['revenue'] = filtered_df['revenue'].astype(float)
        filtered_df['mall'] = filtered_df['mall'].astype(str)
        fig1 = px.line(
            filtered_df, 
            x="time", 
            y="revenue", 
            color='mall',
            color_discrete_sequence=px.colors.qualitative.Plotly,
            labels={'revenue': 'Doanh thu', 'time': 'Tháng', 'mall': 'TTTM'},
            title=f"Doanh thu theo tháng trong năm {selected_value}", 
            markers=True
        )
        # fig1.update_traces(line_color="#1abc9c", marker_color="#16a085")
        fig1.update_layout(template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

    # Orders bar chart
    with col2:
        all_malls_ = df_cat_revenue['mall'].unique().tolist()
        selected_mall = st.selectbox('Trung tâm mua sắm: ', all_malls_)
        fig2 = px.pie(
            df_cat_revenue[df_cat_revenue['mall'] == selected_mall],
            values='revenue',
            names='category',
            title=f'Tỉ trọng doanh thu theo danh mục sản phẩm của Trung tâm mua sắm {selected_mall}',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)

    st.write("---")

with tab2:
    st.write("## **Phân tích RFM (Recency, Frequency, Monetary)**")
    st.write("### ***Trực quan hóa thông số RFM của các trung tâm thương mại***")
    col1, col2 = st.columns(2)
    with col1:
        selected_limit = st.selectbox("Limit: ", [5, 10, 20, 50, 100])
    with col2:
        rfm_mall = st.selectbox('RFM của Trung tâm thương mại: ', all_malls)
    rfm_data = ca.rfm_analysis(rfm_mall, selected_limit)
    df_rfm = pd.DataFrame(rfm_data['rfm_data'])
    df_rfm['monetary'] = pd.to_numeric(df_rfm['monetary'], errors='coerce')
    df_seg = ca.rfm_segmentation(rfm_mall)
    df_segment = pd.DataFrame(df_seg)

    col1, col2 = st.columns(2)
    with col1:
        fig3 = px.scatter(
            df_rfm, 
            x="recency",      
            y="freq",          
            size="monetary", 
            color="monetary",  
            hover_name="customer_id", 
            labels={'recency': 'Thời gian kể từ ngày mua gần nhất', 'freq': 'Tần suất mua hàng'},
            title=f"> RFM của {selected_limit} khách hàng quay lại gần đây nhất của trung tâm thương mại {rfm_mall}",
            size_max=60        
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        fig4 = px.treemap(
            df_segment, 
            path=[px.Constant("RFM"), 'Segment'], 
            values='Count', 
            color='Monetary', 
            color_continuous_scale='RdYlGn',
            title='Phân Tích RFM Segmentation bằng Treemap',
            hover_data={'Count': True, 'Percent': ':.2f%'} 
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    st.write("### ***Thông tin mua sắm của khách hàng***")
    col1, col2 = st.columns(2)
    with st.form(key='rfm'):
        with col1:
            l1, l2, l3 = st.columns(3)
            with l1:
                uid = st.text_input("Mã khách hàng: ")
            with l2:
                gender = st.selectbox("Giới tính",["Male", "Female"])
            with l3:
                age = st.number_input("Tuổi: ", 0, 100)
            l1, l2, l3 = st.columns([2,1,3])
            with l1:
                st.write("**Bill Template: **")

            file_content = ""
            FILE_PATH = os.path.join(os.getcwd(), 'template', 'csv_template.csv') 
            FILE_NAME = "RFM_Template.csv"
            CSV_TYPE = "text/csv"
            XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if not os.path.exists(FILE_PATH):
                st.error(f"Không tìm thấy tệp: {FILE_PATH}. Vui lòng kiểm tra lại đường dẫn.")
                st.stop()

            # 2. Đọc nội dung tệp
            try:
                # Đối với tệp văn bản (CSV, TXT, JSON), đọc dưới dạng chuỗi
                with open(FILE_PATH, "r", encoding='utf-8') as f:
                    file_content = f.read()
                # if file_content == "":
                #     st.warning(f"Fail extract file template {FILE_PATH}")
                # else: st.success(f"Success tracking file {FILE_PATH}")

            except Exception as e:
                st.error(f"Lỗi khi đọc tệp: {e}")
                st.stop()

            if file_content != "":
                with l2:
                    st.download_button(
                        label="CSV",
                        data=file_content, 
                        file_name=FILE_NAME,
                        mime=CSV_TYPE
                    )
                with l3:
                    st.download_button(
                        label="XLSX",
                        data=file_content, 
                        file_name=FILE_NAME,
                        mime=XLSX_TYPE
                    )
            file_uploaded = st.file_uploader("Chọn file các hóa đơn mua sắm (csv | xlsx): ", type=['csv', 'xlsx'], accept_multiple_files=False)

        frfm_submit = st.form_submit_button("Thực hiện")
        if frfm_submit:
            if not file_uploaded:
                st.error("Vui lòng tải lên file hóa đơn mua sắm để phân tích.")
                st.stop()
                
            # 1. Đọc tệp đã tải lên thành DataFrame
            df_transactions = uu.process_file_uploaded(file_uploaded)
                
            if df_transactions is not None:
                st.info(f"Đã đọc thành công {len(df_transactions)} dòng dữ liệu từ tệp: {file_uploaded.name}")
                    
                # 2. Chuẩn bị Payload
                # Payload gửi đi bao gồm metadata (uid, gender, age) và data transactions (dạng JSON string)
                payload = {
                    "customer_id": uid,
                    "gender": gender,
                    "age": age,
                    "transactions": df_transactions.to_json(orient='records') 
                }

                rfm_data = ca.rfm_bill(payload)
            else: st.error("Lỗi hiện thực")

with tab3:
    st.write("## **Mô hình dự đoán khả năng rời bỏ**")
    st.write("### ***Thông số của các mô hình được sử dụng***")
    df_metadata = ca.model_metadata()
    df_metadata = pd.DataFrame(df_metadata)
    df_metadata = df_metadata.drop(columns=['feature_names', 'filename', 'framework', 'metrics'])
    cols = ['algorithm'] + [col for col in df_metadata.columns if col != 'algorithm']

    df_metadata = df_metadata[cols]
    df_render = df_metadata.rename(columns={
        "algorithm": "Mô hình", "f1_score": "F1 Score", "accuracy": "Accuracy", 
        "input_shape": "Input Shape", "precision" :"Precision", "recall": "Recall",
        "target_names": "Nhãn mục tiêu"
    })
    st.write(df_render)
    st.write("---")
    st.write("### ***Dự đoán kết quả với các mô hình trên***")

    col1, col2 = st.columns(2)
    df_pred = None

    with col1:
        with st.form(key='predict'):
            st.write("--- Thông tin tiêu dùng dựa trên RFM ---")
            cola, colb, colc = st.columns(3)
            with cola:
                st.write("> Nhân khẩu học")
                fage = st.number_input("Tuổi của bạn: ", min_value=0, max_value=100)
                fgender = st.selectbox("Giới tính: ",["Male", "Female"])
                
            with colb:
                st.write("> Thông tin mua hàng")
                fmall = st.selectbox("Trung tâm thương mại: ", all_malls)
                fcategory = st.selectbox("Mặt hàng mua gần nhất: ", [item['category'] for item in stats['categories'] if item["mall"] == fmall])
                fpayment = st.selectbox("Phương thức thanh toán: ", stats['payment_method'])

            with colc:
                st.write("> RFM")
                frecency = int(st.number_input("Recency: "))
                ffreq = int(st.number_input("Frequency: "))
                fmon = st.number_input("Monetary: \$")

            fpredict = st.form_submit_button("Tiến hành dự đoán")
        
        if fpredict:
            fdata = {
                "Recency": frecency,
                "Frequency": ffreq,
                "Monetary": fmon,
                "age": fage,
                "gender": fgender,
                "shopping_mall": fmall,
                "category": fcategory,
                "payment_method": fpayment
            }

            df_pred = ca.model_prediction(fdata)
            df_pred = pd.DataFrame(df_pred)

    with col2:
        st.write(df_pred)