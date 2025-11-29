import pandas as pd
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import squarify 
import os

warnings.filterwarnings('ignore')
sns.set(style='whitegrid')

class RFMAnalyzer:
    def __init__(self):
        self.quantiles = None

    def _r_score(self, x, q_dict):
        q = q_dict['Recency']
        if x <= q[.25]: return 1
        elif x <= q[.5]: return 2
        elif x <= q[.75]: return 3
        else: return 4

    def _fm_score(self, x, col, q_dict):
        q = q_dict[col]
        if x <= q[.25]: return 4
        elif x <= q[.5]: return 3
        elif x <= q[.75]: return 2
        else: return 1

    def _define_segment(self, row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']

        # 1. Champions
        if r == 1 and f == 1 and m == 1: return 'Champions'
        # 2. Loyal Customers
        if r in [1, 2] and f in [1, 2] and m in [1, 2]: return 'Loyal Customers'
        # 3. Potential Loyalist
        if r in [1, 2] and f in [1, 3] and m in [1, 3]: return 'Potential Loyalist'
        # 4. Recent Customers
        if r == 1 and f == 4: return 'Recent Customers'
        # 5. Promising
        if r == 2 and m in [3, 4]: return 'Promising'
        # 6. Can't Lose Them
        if r in [3, 4] and f in [1, 2] and m == 1: return "Can't Lose Them"
        # 7. At Risk
        if r == 4 and f in [1, 2] and m in [1, 2]: return 'At Risk'
        # 8. Need Attention
        if r == 3 and f in [2, 3] and m in [2, 3]: return 'Need Attention'
        # 9. Lost
        if r == 4 and f == 4 and m == 4: return 'Lost'
        # 10. Hibernating
        if r == 4 and f in [3, 4] and m in [3, 4]: return 'Hibernating'
        # 11. About To Sleep
        if r in [3, 4] and f in [3, 4] and m in [3, 4]: return 'About To Sleep'

        return 'Other'

    def process(self, df):
        
        # Chia df thành các nhóm theo Mall
        mall_groups = df.groupby('shopping_mall')
        result_list = []
        rfm_range_scoring = []

        for mall_name, group_df in mall_groups:
            # Tính Quantile riêng cho Mall 
            local_quantiles = group_df[['Recency', 'Frequency', 'Monetary']].quantile([.25, .5, .75]).to_dict()

            rfm_item = {
                "mall": mall_name,
                "R": [local_quantiles['Recency'][.25], local_quantiles['Recency'][.5], local_quantiles['Recency'][.75]],
                "F": [local_quantiles['Frequency'][.25], local_quantiles['Frequency'][.5], local_quantiles['Frequency'][.75]],
                "M": [local_quantiles['Monetary'][.25], local_quantiles['Monetary'][.5], local_quantiles['Monetary'][.75]]
            }

            rfm_range_scoring.append(rfm_item)

            group_copy = group_df.copy()
            group_copy['R_Score'] = group_copy['Recency'].apply(self._r_score, args=(local_quantiles,))
            group_copy['F_Score'] = group_copy['Frequency'].apply(self._fm_score, args=('Frequency', local_quantiles))
            group_copy['M_Score'] = group_copy['Monetary'].apply(self._fm_score, args=('Monetary', local_quantiles))
            
            result_list.append(group_copy)

        df_rfm = pd.concat(result_list)
        df_rfm['RFM_Score'] = df_rfm['R_Score'].astype(str) + df_rfm['F_Score'].astype(str) + df_rfm['M_Score'].astype(str)
        df_rfm['Segment'] = df_rfm.apply(self._define_segment, axis=1)
        with open("config/rfm_config.json", 'w') as f:
            f.write(rfm_range_scoring)
            
        return df_rfm

    def _process_global(self, df):
        df_rfm = df.copy()
        self.quantiles = df_rfm[['Recency', 'Frequency', 'Monetary']].quantile([.25, .5, .75]).to_dict()
        df_rfm['R_Score'] = df_rfm['Recency'].apply(self._r_score, args=(self.quantiles,))
        df_rfm['F_Score'] = df_rfm['Frequency'].apply(self._fm_score, args=('Frequency', self.quantiles))
        df_rfm['M_Score'] = df_rfm['Monetary'].apply(self._fm_score, args=('Monetary', self.quantiles))
        df_rfm['RFM_Score'] = df_rfm['R_Score'].astype(str) + df_rfm['F_Score'].astype(str) + df_rfm['M_Score'].astype(str)
        df_rfm['Segment'] = df_rfm.apply(self._define_segment, axis=1)
        return df_rfm

    def segmentation(self, df_labeled):
        print("\n" + "-"*30)
        print("Thống kê phân khúc khách hàng")
        print("-" * 30)
        
        # Thống kê số lượng
        segment_counts = df_labeled['Segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Count']
        segment_counts['Percent'] = round((segment_counts['Count'] / segment_counts['Count'].sum()) * 100, 2)
        print(segment_counts)

        # Thống kê chỉ số trung bình
        print("\n--- Chỉ số trung bình từng nhóm ---")
        segment_stats = df_labeled.groupby('Segment')[['Recency', 'Frequency', 'Monetary']].mean().round(1)
        print(segment_stats)

        df_rfm = pd.merge(segment_counts, segment_stats, on="Segment")

        return df_rfm

    def visualize(self, df_labeled):
        print("\n" + "-"*30)
        print("Thống kê phân khúc khách hàng")
        print("-" * 30)
        
        segment_counts = df_labeled['Segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Count']
        segment_counts['Percent'] = (segment_counts['Count'] / segment_counts['Count'].sum()) * 100
        print(segment_counts)

        print("\n--- Chỉ số trung bình từng nhóm ---")
        segment_stats = df_labeled.groupby('Segment')[['Recency', 'Frequency', 'Monetary']].mean().round(1)
        print(segment_stats)

        plt.figure(figsize=(14, 8))
        colors = sns.color_palette('Spectral', len(segment_counts))
        squarify.plot(sizes=segment_counts['Count'], label=segment_counts['Segment'], 
                      alpha=0.8, color=colors, value=segment_counts['Percent'].apply(lambda x: f"{x:.1f}%"))
        plt.title('Phân bổ các phân khúc khách hàng (Theo Mall)', fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('segment_treemap.png', dpi=300)
        print("\n-> Đã lưu biểu đồ: segment_treemap.png")

        plt.figure(figsize=(12, 6))
        order = segment_stats.sort_values('Monetary', ascending=False).index
        sns.barplot(x=segment_stats.loc[order].index, y=segment_stats.loc[order]['Monetary'], palette='viridis')
        plt.title('Giá trị chi tiêu trung bình (Monetary)', fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('segment_monetary.png', dpi=300)
        print("-> Đã lưu biểu đồ: segment_monetary.png")

if __name__ == "__main__":
    FILE_NAME = "sales_mart.csv"
    
    if os.path.exists(FILE_NAME):
        print(f"--- Đang xử lý file: {FILE_NAME} ---")
        df = pd.read_csv(FILE_NAME)
        
        analyzer = RFMAnalyzer()
        df_result = analyzer.process(df)
        analyzer.visualize(df_result)
        
        df_result.to_csv("customer_segments.csv", index=False)
        print("-> Đã lưu kết quả phân loại vào: customer_segments.csv")
        
    else:
        print(f"LỖI: Không tìm thấy file {FILE_NAME}")