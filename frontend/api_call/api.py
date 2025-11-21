import requests as rqs

class Api:
    def __init__(self, st):
        self.st = st
        self.api_url = "http://127.0.0.1:5000"

    def get_all_transactions(self, page = 1, limit = 10):
        try:
            res = rqs.get(self.api_url + f"/api/retail?page={page}&per_page={limit}", timeout=5)
            res.raise_for_status()
            data = res.json()
            self.st.success("✅ Dữ liệu tải thành công!")
            return data

        except rqs.exceptions.RequestException as e:
            self.st.error(f"Error: {e}")

    def stats_counting(self, mode = "all"):
        try:
            res = rqs.get(self.api_url + f"/api/count-transactions?mode={mode}")
            res.raise_for_status()
            data = res.json()
            self.st.success("✅ Dữ liệu tải thành công!")
            return data
        
        except rqs.exceptions.RequestException as e:
            self.st.error(f"Error: {e}")

    def revenue_in_year_by_month(self, year = 2024):
        try:
            res = rqs.get(self.api_url+ f"/api/revenue-by-month?year={year}")
            res.raise_for_status()
            data = res.json()
            self.st.success("✅ Dữ liệu tải thành công!")
            return data
        except rqs.exceptions.RequestException as e:
            self.st.error(f"Error: {e}")

    def rfm_analysis(self, limit = 50):
        try:
            res =rqs.get(self.api_url + f"/api/rfm?limit={limit}")
            res.raise_for_status()
            data = res.json()
            self.st.success("✅ Dữ liệu tải thành công!")
            return data
        except rqs.exceptions.RequestException as e:
            self.st.error(f"Error: {e}")
