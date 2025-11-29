from datetime import datetime

def time_convert(date_str):
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")

    # 2. Tách các thành phần
    ngay = date_obj.day
    thang = date_obj.month
    nam = date_obj.year
    quy = (thang - 1) // 3 + 1 # Công thức tính quý

    return ngay, thang, nam, quy