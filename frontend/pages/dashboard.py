import streamlit as st
import pandas as pd
import plotly.express as px
from api_call.api import Api

# --- CONFIG ---

st.set_page_config(page_title="Business Dashboard", layout="wide")
st.markdown("<h1 style='text-align:center;'>📈 Business Overview Dashboard</h1>", unsafe_allow_html=True)
st.write("")
api = Api(st)

# --- API CALL ---
transactions = api.get_all_transactions()
stats = api.stats_counting()

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
selected_year = st.selectbox("Year: ", stats['years'])
monthly_revenue = api.revenue_in_year_by_month(selected_year)
df_monthly_revenue = pd.DataFrame(monthly_revenue['revenue_monthly'])

df_cat_revenue = pd.DataFrame(monthly_revenue['revenue_cat'])
st.write(df_monthly_revenue)

# --- CHARTS ---
col1, col2 = st.columns(2)
with col1:
    all_malls = df_monthly_revenue['shopping_mall'].unique().tolist()
    selected_malls = st.multiselect(
        "Chọn Mall để hiển thị:",
        options=all_malls,
        default=all_malls[:3] # Mặc định hiện Top 5
    )
    filtered_df = df_monthly_revenue[df_monthly_revenue['shopping_mall'].isin(selected_malls)]
    filtered_df['totalamount'] = filtered_df['totalamount'].astype(float)
    filtered_df['shopping_mall'] = filtered_df['shopping_mall'].astype(str)
    fig1 = px.line(
        filtered_df, 
        x="month", 
        y="totalamount", 
        color='shopping_mall',
        color_discrete_sequence=px.colors.qualitative.Plotly,
        labels={'totalamount': 'Doanh thu', 'month': 'Tháng', 'shopping_mall': 'TTTM'},
        title=f"Doanh thu theo tháng trong năm {selected_year}", 
        markers=True
    )
    # fig1.update_traces(line_color="#1abc9c", marker_color="#16a085")
    fig1.update_layout(template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

# Orders bar chart
with col2:
    all_malls_ = df_cat_revenue['shopping_mall'].unique().tolist()
    selected_mall = st.selectbox('Trung tâm mua sắm: ', all_malls_)
    fig2 = px.pie(
        df_cat_revenue[df_cat_revenue['shopping_mall'] == selected_mall],
        values='totalamount',
        names='category',
        title=f'Tỉ trọng doanh thu theo danh mục sản phẩm của Trung tâm mua sắm {selected_mall}',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig2, use_container_width=True)

st.write("---")
st.write("## **Phân tích RFM (Recency, Frequency, Monetary)**")
col1, col2 = st.columns(2)
with col1:
    selected_limit = st.selectbox("Limit: ", [5, 10, 20, 50, 100])
with col2:
    rfm_mall = st.selectbox('RFM của Trung tâm thương mại: ', all_malls)
rfm_data = api.rfm_analysis(rfm_mall, selected_limit)
df_rfm = pd.DataFrame(rfm_data['rfm_data'])
df_rfm['monetary'] = pd.to_numeric(df_rfm['monetary'], errors='coerce')

fig3 = px.scatter(
    df_rfm, 
    x="recency",      
    y="freq",          
    size="monetary", 
    color="monetary",  
    hover_name="customer_id", 
    labels={'recency': 'Thời gian kể từ ngày mua gần nhất', 'freq': 'Tần suất mua hàng'},
    title=f"RFM của {selected_limit} khách hàng quay lại gần đây nhất của trung tâm thương mại {rfm_mall}",
    size_max=60        
)
st.plotly_chart(fig3, use_container_width=True)