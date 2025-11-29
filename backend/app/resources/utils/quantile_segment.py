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
        r, f, m = row['R'], row['F'], row['M']

        # 1. Champions (Vô địch)
        if r == 1 and f == 1 and m == 1: return 'Champions'
        
        # 2. Loyal Customers (Trung thành)
        if r in [1, 2] and f in [1, 2] and m in [1, 2]: return 'Loyal Customers'
        
        # 3. Potential Loyalist (Tiềm năng)
        if r in [1, 2] and f in [1, 3] and m in [1, 3]: return 'Potential Loyalist'
        
        # 4. Recent Customers (Khách mới)
        if r == 1 and f == 4: return 'Recent Customers'
        
        # 5. Promising (Hứa hẹn)
        if r == 2 and m in [3, 4]: return 'Promising'
        
        # 6. Can't Lose Them
        if r in [3, 4] and f in [1, 2] and m == 1: return "Can't Lose Them"
        
        # 7. At Risk (Rủi ro)
        if r == 4 and f in [1, 2] and m in [1, 2]: return 'At Risk'
        
        # 8. Need Attention (Cần chú ý)
        if r == 3 and f in [2, 3] and m in [2, 3]: return 'Need Attention'
        
        # 9. Lost (Đã mất)
        if r == 4 and f == 4 and m == 4: return 'Lost'
        
        # 10. Hibernating (Ngủ đông)
        if r == 4 and f in [3, 4] and m in [3, 4]: return 'Hibernating'
        
        # 11. About To Sleep (Sắp ngủ)
        if r in [3, 4] and f in [3, 4] and m in [3, 4]: return 'About To Sleep'

        return 'Other'

    def process(self, df):
        df_rfm = df.copy()
        
        # Tính Quantiles
        self.quantiles = df_rfm[['Recency', 'Frequency', 'Monetary']].quantile([.25, .5, .75]).to_dict()
        df_rfm['R'] = df_rfm['Recency'].apply(self._r_score, args=(self.quantiles,))
        df_rfm['F'] = df_rfm['Frequency'].apply(self._fm_score, args=('Frequency', self.quantiles))
        df_rfm['M'] = df_rfm['Monetary'].apply(self._fm_score, args=('Monetary', self.quantiles))
        df_rfm['RFM_Score'] = df_rfm['R'].astype(str) + df_rfm['F'].astype(str) + df_rfm['M'].astype(str)
        
        # Phân loại
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

if __name__ == "__main__":
    FILE_NAME = "sales_mart.csv"
    
    if os.path.exists(FILE_NAME):
        print(f"--- Đang xử lý file: {FILE_NAME} ---")
        
        # 1. Load dữ liệu
        df = pd.read_csv(FILE_NAME)
        
        # 2. Khởi tạo bộ phân tích
        analyzer = RFMAnalyzer()
        
        # 3. Xử lý
        df_result = analyzer.process(df)
        
        # 4. Vẽ biểu đồ báo cáo
        analyzer.visualize(df_result)
        
        # 5. Lưu kết quả ra CSV mới 
        df_result.to_csv("customer_segments.csv", index=False)
        print("-> Đã lưu kết quả phân loại vào: customer_segments.csv")
        
    else:
        print(f"LỖI: Không tìm thấy file {FILE_NAME}")