import joblib
import pandas as pd
import numpy as np

# 1. Load Encoder và Model ra phạm vi toàn cục (Global)
# Để chỉ load 1 lần duy nhất khi khởi động Server
try:
    ENCODERS_DICT = joblib.load("encoder/encoder.pkl")
    print("✅ Đã load Encoder thành công!")
except Exception as e:
    print(f"❌ Lỗi load Encoder: {e}")
    ENCODERS_DICT = {}

cols_to_encode = ['gender', 'shopping_mall', 'payment_method', 'category']

def encoding(df):
    # Copy để tránh warning SettingWithCopy của Pandas
    df_out = df.copy()
    
    for col in cols_to_encode:
        # Tạo key để lấy đúng encoder (vd: gender -> gender_code)
        key_name = f'{col}_code'
        
        if key_name in ENCODERS_DICT:
            le = ENCODERS_DICT[key_name]
            
            # Kỹ thuật Safe Transform: Xử lý giá trị lạ (Unseen labels)
            # Lấy danh sách các class đã học (vd: ['Female', 'Male'])
            classes = le.classes_.tolist()
            
            # Hàm apply để check từng dòng: 
            # Nếu giá trị x nằm trong classes -> transform bình thường
            # Nếu không -> Gán giá trị mặc định (ví dụ -1 hoặc 0) để không bị crash
            df_out[key_name] = df_out[col].apply(
                lambda x: le.transform([x])[0] if x in classes else -1
            )
        else:
            print(f"⚠️ Cảnh báo: Không tìm thấy encoder cho {key_name}")
            df_out[key_name] = -100 # Giá trị fallback
            
    # Bỏ cột gốc, giữ lại cột _code
    return df_out.drop(columns=cols_to_encode)