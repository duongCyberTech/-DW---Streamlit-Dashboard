import requests as rqs
import pandas as pd
import streamlit as st

class Api:
    def __init__(self):
        self.api_url = "http://localhost:5000"
        self.ml_url = "http://localhost:5001"
        self.pred_lst = [{
                "full": 'K Nearest Neighbors',
                "short": 'knn'
            }, {
                "full": 'Extreme Gradient Boosting',
                "short": 'xgboost'
            }, {
                "full": 'Random Forest',
                "short": 'rf'
            }, {
                "full": 'Decision Tree',
                "short": 'dt'
            }
        ]

    def get_all_transactions(self, page = 1, limit = 10):
        try:
            res = rqs.get(self.api_url + f"/api/retail?page={page}&per_page={limit}", timeout=5)
            res.raise_for_status()
            data = res.json()
            # st.success("✅ Dữ liệu tải thành công!")
            return data

        except rqs.exceptions.RequestException as e:
            st.error(f"Error: {e}")

    def stats_counting(self, mode = "all"):
        try:
            res = rqs.get(self.api_url + f"/api/count-transactions?mode={mode}")
            res.raise_for_status()
            data = res.json()
            # st.success("✅ Dữ liệu tải thành công!")
            return data
        
        except rqs.exceptions.RequestException as e:
            st.error(f"Error: {e}")

    def revenue_in_year_by_month(self, time_value = 2023, period = 'monthly'):
        try:
            res = rqs.get(self.api_url+ f"/api/revenue-by-month?time_value={time_value}&period={period}")
            res.raise_for_status()
            data = res.json()
            # st.success("✅ Dữ liệu tải thành công!")
            return data
        except rqs.exceptions.RequestException as e:
            st.error(f"Error: {e}")

    def rfm_bill(self, data):
        try:
            res = rqs.post(self.api_url + f"/api/retail", json=data)
            res.raise_for_status()
            data = res.json()
            return data
        except rqs.exceptions.RequestException as e:
            print(f"Lỗi: {e}")

    def rfm_analysis(self, mall, limit = 50):
        try:
            if mall == None:
                res =rqs.get(self.api_url + f"/api/rfm?limit={limit}")
            else: res =rqs.get(self.api_url + f"/api/rfm?limit={limit}&mall={mall}")
            res.raise_for_status()
            data = res.json()
            # st.success("✅ Dữ liệu tải thành công!")
            return data
        except rqs.exceptions.RequestException as e:
            st.error(f"Error: {e}")

    def rfm_segmentation(self, mall):
        try:
            res = rqs.get(self.api_url + f"/api/rfm-segmentation?mall={mall}")
            res.raise_for_status()
            res = res.json()
            res = res['rfm']
            
            return res
        except rqs.exceptions.RequestException as e:
            st.error(f"Error: {e}")

    def model_metadata(self):
        try:
            res = rqs.get(self.ml_url + "/api/metadata")
            res.raise_for_status()
            data = res.json()
            return data 
        except rqs.exceptions.RequestException as e:
            st.error(f"Error: {e}")

    def model_prediction(self, data):
        df_pred = []
        for model in self.pred_lst:
            try:
                res = rqs.post(self.ml_url + f"/api/predict/{model['short']}",json=data)
                res = res.json()
                print(res)
                df_pred.append({
                    "Mô hình": model["full"], 
                    "Giá trị dự đoán": "Ở lại" if res['pred'] == 0 else "Rời bỏ", 
                    "Xác suất xảy ra": res['prob'] if res['pred'] == 1 else (1 - res['prob'])
                })
            except rqs.exceptions.RequestException as e:
                st.error(f"Fail while training {model}")
                continue
        print(df_pred)
        return df_pred