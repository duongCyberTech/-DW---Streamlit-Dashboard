import csv
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.neighbors import NearestCentroid,NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.preprocessing import Normalizer,LabelEncoder
from sklearn.metrics import accuracy_score,confusion_matrix,ConfusionMatrixDisplay,classification_report
from sklearn.utils.extmath import randomized_svd
from IPython.display import display
from numpy import linalg as la
from pulp import *
import seaborn as sns
from scipy.sparse import csr_matrix
pd.set_option('display.max_colwidth',None)
import os

custom_df = pd.read_csv('./DM_customer_profile.csv',sep=",",on_bad_lines="skip",encoding='utf-8-sig')
# custom_df.info()
# custom_df.head(10)

def calculate_monthly_profit(input):
    df = input.copy()
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce', format="%d-%m-%Y")
    df = df.dropna(subset=['invoice_date'])

    df['year_month'] = df['invoice_date'].dt.strftime('%Y-%m')

    profit_series = df.groupby('year_month')['totalamount'].sum()
    profit_list = profit_series.tolist()
    return profit_list, profit_series.index.tolist()

def calculate_quarter_profit(input):
    df = input.copy()
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce', format="%d-%m-%Y")
    df = df.dropna(subset=['invoice_date'])

    df = df.sort_values(by='invoice_date')
    df['quarter'] = df['invoice_date'].dt.to_period('Q')

    profit_series = df.groupby('quarter')['totalamount'].sum()
    profit_list = profit_series.tolist()
    profit_label_list = [str(i) for i in profit_series.index]
    return profit_list, profit_label_list

def calculate_year_profit(input):
    df = input.copy()
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce', format="%d-%m-%Y")
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

# monthly_profit, months = calculate_monthly_profit(custom_df)
# n_months = len(months)

# plt.bar(months[:-1], monthly_profit[:-1])
# plt.xlabel("Months")
# plt.ylabel("Profit")
# plt.title("Profit in each month")
# plt.tight_layout()
# plt.xticks(
#     ticks=range(0, n_months, 3),
#     labels=[months[i] for i in range(0, n_months, 3)],
#     rotation=45,
#     ha='right'
# )
# plt.show()

# quarter_profit, quarters = calculate_quarter_profit(custom_df)
# n_quarters = len(quarters)

# plt.bar(quarters, quarter_profit)
# plt.xlabel("Quarter")
# plt.ylabel("Profit")
# plt.title("Profit in each quarter")
# plt.tight_layout()
# plt.xticks(
#     ticks=range(0, n_quarters),
#     labels=[quarters[i] for i in range(0, n_quarters)],
#     rotation=45,
#     ha='right'
# )
# plt.show()

# year_profit, years = calculate_year_profit(custom_df)
# n_years = len(years)

# plt.bar(years, year_profit)
# plt.xlabel("Year")
# plt.ylabel("Profit")
# plt.title("Profit in each year")
# plt.tight_layout()
# plt.xticks(
#     ticks=range(0, n_years),
#     labels=[years[i] for i in range(0, n_years)],
#     rotation=45,
#     ha='right'
# )
# plt.show()

# mall_profit, malls = calculate_mall_profit(custom_df)
# n_malls = len(malls)

# plt.bar(malls, mall_profit)
# plt.xlabel("Mall name")
# plt.ylabel("Profit")
# plt.title("Profit in each mall")
# plt.tight_layout()
# plt.xticks(
#     ticks=range(0, n_malls),
#     labels=malls,
#     rotation=45,
#     ha='right'
# )
# plt.show()


"""**Kịch bản**

Tăng số lượng mua hàng (hoặc số tiền mỗi mặt hàng) ở một số mall để lợi nhuận cao nhất
- Chọn một 3/10 mall để tăng 20% số lượng hàng hóa bán
- Tăng trên toàn bộ loại mặt hàng (hoặc một số loại mặt hàng)
- Để tăng thì cần đầu tư. Và đầu tư cần 20% profit. Kinh phí không quá 10M
"""

# Number of increasing mall in scenanio
k = 5
# Percentage of profit increasing
percent = 0.4
# Budget limit
fee_percent = 0.3
budget = 10 * 10**6
# Category limit ['Clothing', 'Shoes', 'Books', 'Cosmetics', 'Food & Beverage', 'Toys', 'Technology', 'Souvenir']
category_limit = ['Clothing', 'Shoes', 'Books', 'Cosmetics', 'Food & Beverage', 'Toys', 'Technology', 'Souvenir']
# Mandatory to increase at mall ['Cevahir AVM', 'Emaar Square Mall', 'Forum Istanbul', 'Istinye Park', 'Kanyon', 'Mall of Istanbul', 'Metrocity', 'Metropol AVM', 'Viaport Outlet', 'Zorlu Center']
mandatory_at_mall = []


def get_list_opprice():
  df_to_increase = custom_df.copy()

  is_in_target_cate = df_to_increase['category'].isin(category_limit)
  df_to_increase.loc[is_in_target_cate, 'quantity'] = df_to_increase.loc[is_in_target_cate, 'quantity'].apply( lambda x : math.floor(x * percent))
  df_to_increase.loc[is_in_target_cate, 'totalamount'] = (df_to_increase.loc[is_in_target_cate, 'quantity'] * df_to_increase.loc[is_in_target_cate,'price'])

  list_optimize_price = df_to_increase.groupby('shopping_mall')[['totalamount','quantity']].sum()
  return list_optimize_price.index.array.tolist(), list_optimize_price

list_malls, list_optimize_price = get_list_opprice()
expected_revenue = list_optimize_price['totalamount'].to_dict()

prob = LpProblem("Optimal_Mall_Selection", LpMaximize)
mall_vars = LpVariable.dicts("Select_Mall_To_Optimize", list_malls, 0, 1, LpBinary)

# Target function
prob += lpSum([expected_revenue[m] * mall_vars[m] for m in list_malls]), "Total_Expected_Profit"

# Contraint function
if(len(mandatory_at_mall) <= k):
  for m in mandatory_at_mall:
    if m in list_malls:
      prob += mall_vars[m] == 1, f"Mandatory_Mall_{m}"
prob += lpSum([mall_vars[m] for m in list_malls]) <= k, "Select_k_Malls" # limit number of malls
prob += lpSum([expected_revenue[m]/percent * fee_percent * mall_vars[m] for m in list_malls]) <= budget, "Budget_limit" # limit

prob.solve(PULP_CBC_CMD(msg=False))

print(f"Trạng thái giải: {LpStatus[prob.status]}")
total_profit = custom_df['totalamount'].sum() + value(prob.objective)
print(f"Lợi nhuận tối đa: {total_profit:,.0f} USD")
budget_value = prob.constraints['Budget_limit'].value()
print(f"Tổng chi phí là: {math.floor(budget + (budget_value or 0)):,} USD")

optimal_malls = []
for m in list_malls:
    if mall_vars[m].varValue == 1.0:
        optimal_malls.append(m)
print(f"\nTổ hợp Tối ưu: {optimal_malls}")


# MONTE CARLO config
num_simulations = 100000
mean_growth = fee_percent     # precent increase
std_dev_growth = 0.2        # std of increase present

simulated_profits = []
for i in range(num_simulations):
    scenario_profit = 0
    for mall in optimal_malls:
        # create random increase precent
        random_growth = np.random.normal(mean_growth, std_dev_growth)

        gain = expected_revenue[mall]
        cost = expected_revenue[mall]/percent * random_growth

        net_profit = gain - cost
        scenario_profit += net_profit

    simulated_profits.append(scenario_profit)

# Metric unit
simulated_profits = np.array(simulated_profits)
avg_profit = np.mean(simulated_profits)
min_profit = np.min(simulated_profits)
prob_loss = np.mean(simulated_profits < 0) * 100

print(f"--- KẾT QUẢ MONTE CARLO ({num_simulations} lần chạy) ---")
print(f"Lợi nhuận trung bình kỳ vọng: {avg_profit:,.0f} USD")
print(f"Xác suất bị LỖ VỐN: {prob_loss:.2f}%") # Quan trọng nhất!
print(f"Lợi nhuận xấu nhất (Worst Case): {min_profit:,.0f} USD")

# Vẽ biểu đồ phân phối
plt.figure(figsize=(10, 6))
sns.histplot(simulated_profits, kde=True, color='blue', bins=50)
plt.axvline(0, color='red', linestyle='--', linewidth=2, label='Điểm Hòa Vốn')
plt.axvline(float(avg_profit), color='green', linestyle='-', linewidth=2, label='Lợi nhuận TB')
plt.title('Phân phối Lợi nhuận Dự kiến (Mô phỏng Monte Carlo)')
plt.xlabel('Lợi nhuận Ròng (Net Profit)')
plt.ylabel('Tần suất')
plt.legend()
plt.show()















