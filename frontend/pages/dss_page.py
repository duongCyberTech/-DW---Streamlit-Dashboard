import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pulp import *
import math

st.set_page_config(layout="centered")

# Load data
@st.cache_data
def load_data():
    custom_df = pd.read_csv('dss/DM_customer_profile.csv', sep=",", on_bad_lines="skip", encoding='utf-8-sig')
    custom_df['invoice_date'] = pd.to_datetime(custom_df['invoice_date'], errors='coerce', format="%d/%m/%Y")
    custom_df = custom_df.dropna(subset=['invoice_date'])
    return custom_df

custom_df = load_data()

st.title("Mall Profit Optimization")

# tab1, tab2 = st.tabs(["Optimization", "Sales Analytics"])

# Parameters
st.sidebar.header("Parameters")
k = st.sidebar.slider("Number of malls to increase (k)", 1, 10, 5, help="The number of shopping malls to select for optimization. This determines how many malls will have their prices increased.")
percent = st.sidebar.slider("Increase percentage", 0.1, 1.0, 0.4, help="The percentage by which to increase the quantity sold in selected categories. For example, 0.4 means 40% increase.")
fee_percent = st.sidebar.slider("Investments percentage", 0.1, 1.0, 0.3, help="The percentage of investment cost relative to the expected revenue. Used in budget calculations.")
budget = st.sidebar.number_input("Budget limit", value=10000000, help="The maximum budget available for investments in the selected malls.")

st.sidebar.subheader("Category Limit", help="Select the product categories to apply the price increase to. Only selected categories will be optimized.")
categories = custom_df['category'].unique().tolist()
all_selected = st.sidebar.checkbox("Select All Categories", value=True)
if all_selected:
    category_limit = categories
else:
    category_limit = []
    for cat in categories:
        if st.sidebar.checkbox(cat, value=(cat in categories)):
            category_limit.append(cat)

malls = custom_df['shopping_mall'].unique().tolist()
st.sidebar.subheader("Mall selected", help="Select the product categories to apply the price increase to. Only selected categories will be optimized.")
selected_malls = st.sidebar.multiselect(
    "Mall selected",
    label_visibility="collapsed",
    options=malls,
    max_selections=k
)

# Functions
def get_list_opprice(df, percent, category_limit):
    df_to_increase = df.copy()
    is_in_target_cate = df_to_increase['category'].isin(category_limit)
    df_to_increase.loc[is_in_target_cate, 'quantity'] = df_to_increase.loc[is_in_target_cate, 'quantity'].apply(lambda x: math.floor(x * percent))
    df_to_increase.loc[is_in_target_cate, 'totalamount'] = (df_to_increase.loc[is_in_target_cate, 'quantity'] * df_to_increase.loc[is_in_target_cate, 'price'])
    list_optimize_price = df_to_increase.groupby('shopping_mall')[['totalamount', 'quantity']].sum()
    return list_optimize_price.index.tolist(), list_optimize_price

def calculate_daily_profit(input):
    df = input.copy()
    df = df.dropna(subset=['invoice_date'])
    df['date'] = df['invoice_date'].dt.strftime('%Y-%m-%d')
    profit_series = df.groupby('date')['totalamount'].sum()
    profit_list = profit_series.tolist()
    return profit_list, profit_series.index.tolist()

def calculate_weekly_profit(input):
    df = input.copy()
    df = df.dropna(subset=['invoice_date'])
    df['year_week'] = df['invoice_date'].dt.strftime('%Y-%U')
    profit_series = df.groupby('year_week')['totalamount'].sum()
    profit_list = profit_series.tolist()
    return profit_list, profit_series.index.tolist()

def calculate_monthly_profit(input):
    df = input.copy()
    df = df.dropna(subset=['invoice_date'])
    df['year_month'] = df['invoice_date'].dt.strftime('%Y-%m')
    profit_series = df.groupby('year_month')['totalamount'].sum()
    profit_list = profit_series.tolist()
    return profit_list, profit_series.index.tolist()

def calculate_quarter_profit(input):
    df = input.copy()
    df = df.dropna(subset=['invoice_date'])
    df = df.sort_values(by='invoice_date')
    df['quarter'] = df['invoice_date'].dt.to_period('Q')
    profit_series = df.groupby('quarter')['totalamount'].sum()
    profit_list = profit_series.tolist()
    profit_label_list = [str(i) for i in profit_series.index]
    return profit_list, profit_label_list

def calculate_year_profit(input):
    df = input.copy()
    df = df.dropna(subset=['invoice_date'])
    df['year'] = df['invoice_date'].dt.strftime('%Y')
    profit_series = df.groupby('year')['totalamount'].sum()
    profit_list = profit_series.tolist()
    return profit_list, profit_series.index.tolist()

def calculate_mall_profit(input):
    df = input.copy()
    profit_series = df.groupby('shopping_mall')['totalamount'].sum()
    profit_list = profit_series.tolist()
    return profit_list, profit_series.index.tolist()

# with tab1:
if st.button("Run Optimization"):
    list_malls, list_optimize_price = get_list_opprice(custom_df, percent, category_limit)
    expected_revenue = list_optimize_price['totalamount'].to_dict()

    prob = LpProblem("Optimal_Mall_Selection", LpMaximize)
    mall_vars = LpVariable.dicts("Select_Mall_To_Optimize", list_malls, 0, 1, LpBinary)
    # Target function
    prob += lpSum([expected_revenue[m] * mall_vars[m] for m in list_malls]), "Total_Expected_Profit"
    # Contraint function
    if(len(selected_malls) <= k):
        for m in selected_malls:
            if m in list_malls:
                prob += mall_vars[m] == 1, f"Mandatory_Mall_{m}"
    prob += lpSum([mall_vars[m] for m in list_malls]) <= k, "Select_k_Malls"
    prob += lpSum([expected_revenue[m] / percent * fee_percent * mall_vars[m] for m in list_malls]) <= budget, "Budget_limit"

    prob.solve(PULP_CBC_CMD(msg=False))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Optimization Status", LpStatus[prob.status])
        total_profit = custom_df['totalamount'].sum() + value(prob.objective)
        st.metric("Total Profit", f"{total_profit:,.0f} USD")
    with col2:
        budget_value = prob.constraints['Budget_limit'].value()
        st.metric("Total Cost", f"{math.floor(budget + (budget_value or 0)):,.0f} USD")

    optimal_malls = [m for m in list_malls if mall_vars[m].varValue == 1.0]
    st.subheader("Optimal Malls Selected")
    st.markdown("\n".join(f"- {mall}" for mall in optimal_malls))

    # Monte Carlo
    st.subheader("Monte Carlo Simulation Results")
    num_simulations = 10000
    mean_growth = fee_percent
    std_dev_growth = 0.2
    simulated_profits = []
    for i in range(num_simulations):
        scenario_profit = 0
        for mall in optimal_malls:
            random_growth = np.random.normal(mean_growth, std_dev_growth)
            gain = expected_revenue[mall]
            cost = expected_revenue[mall] / percent * random_growth
            net_profit = gain - cost
            scenario_profit += net_profit
        simulated_profits.append(scenario_profit)

    simulated_profits = np.array(simulated_profits)
    avg_profit = np.mean(simulated_profits)
    prob_loss = np.mean(simulated_profits < 0) * 100
    min_profit = np.min(simulated_profits)

    col3, col4 = st.columns(2)
    with col3:
        st.metric("Avg Expected Profit", f"{avg_profit:,.0f} USD", delta=f"{prob_loss:.2f}% Loss Prob")
        if prob_loss > 50:
            st.metric("Loss Probability", f"{prob_loss:.2f}%", delta="High Risk", delta_color="inverse")
        else:
            st.metric("Loss Probability", f"{prob_loss:.2f}%", delta="Acceptable")
    with col4:
        st.metric("Worst Case Profit", f"{min_profit:,.0f} USD")

    # Plot
    fig, ax = plt.subplots()
    sns.histplot(simulated_profits, kde=True, color='blue', bins=50, ax=ax)
    ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Break-even')
    ax.axvline(float(avg_profit), color='green', linestyle='-', linewidth=2, label='Average Profit')
    ax.set_title('Profit Distribution (Monte Carlo)')
    ax.set_xlabel('Net Profit')
    ax.set_ylabel('Frequency')
    ax.legend()
    st.pyplot(fig)

# with tab2:
#     st.header("Sales Analytics")

#     period = st.selectbox("Select Period", ["Day", "Week", "Month", "Quarter", "Year", "Mall"])

#     if period == "Day":
#         profits, labels = calculate_daily_profit(custom_df)
#     elif period == "Week":
#         profits, labels = calculate_weekly_profit(custom_df)
#     elif period == "Month":
#         profits, labels = calculate_monthly_profit(custom_df)
#     elif period == "Quarter":
#         profits, labels = calculate_quarter_profit(custom_df)
#     elif period == "Year":
#         profits, labels = calculate_year_profit(custom_df)
#     elif period == "Mall":
#         profits, labels = calculate_mall_profit(custom_df)

#     # Display data
#     st.subheader("Profit Data")
#     st.dataframe(pd.DataFrame({"Period": labels, "Profit": profits}))

#     # Plot
#     fig, ax = plt.subplots()
#     if period == "Mall":
#         ax.bar(labels, profits)
#         ax.set_title("Profit by Mall")
#         ax.set_xlabel("Mall")
#         ax.set_ylabel("Profit")
#     else:
#         ax.bar(labels, profits)
#         ax.set_title(f"Profit by {period}")
#         ax.set_xlabel(period)
#         ax.set_ylabel("Profit")
#     len_label = len(labels)
#     step = int(len_label / 10) or 1
#     plt.xticks(
#         ticks=range(0, len_label, step),
#         labels=[labels[i] for i in range(0, len_label, step)],
#         rotation=45,
#         ha='right'
#     )
#     st.pyplot(fig)