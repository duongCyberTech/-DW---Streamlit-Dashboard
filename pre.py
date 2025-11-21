import pandas as pd

# 1️⃣ Đọc CSV gốc
df = pd.read_csv("C:\\Users\\admin\\Downloads\\sales_bill.csv")

# 2️⃣ Chuyển đổi cột invoice_date sang format YYYY-MM-DD
df['invoice_date'] = pd.to_datetime(df['invoice_date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

# 3️⃣ (Tùy chọn) Xem dữ liệu
print(df.head())

# 4️⃣ Ghi CSV mới (không ghi index)
df.to_csv("C:\\Users\\admin\\Downloads\\sales_bill.csv", index=False)