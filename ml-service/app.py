from flask import Flask, jsonify, request
import joblib
import os
import glob
import pandas as pd
import requests as rqs
from encoder.encoding import encoding

app = Flask(__name__)
folder_path = 'model'

@app.route('/api/predict/rf', methods=['POST'])
def rf_predict():
    try:
        data = request.json
        df = pd.DataFrame([data])
        df = encoding(df)
        print(df)
        model = joblib.load('./model/rf.pkl')
        rf_model = model['model']
        if not rf_model:
            return
        # 1. Dự đoán class: Kết quả là numpy.int64 -> Cần ép về int()
        prediction = rf_model.predict(df)[0]
        pred_native = int(prediction) 
        
        # 2. Dự đoán xác suất: Kết quả là numpy.ndarray -> Cần chuyển về list()
        probability = rf_model.predict_proba(df)[0]
        prob_native = probability.tolist() 
        
        # Trả về các biến Python native
        return jsonify({
            "pred": pred_native,
            "prob": prob_native[1]
        })
    except rqs.exceptions.RequestException as e:
        print(f"Lỗi: {e}")

@app.route('/api/predict/dt', methods=['POST'])
def dt_predict():
    try:
        data = request.json
        df = pd.DataFrame([data])
        df = encoding(df)
        print(df)
        model = joblib.load('./model/dt.pkl')
        rf_model = model['model']
        if not rf_model:
            return
        # 1. Dự đoán class: Kết quả là numpy.int64 -> Cần ép về int()
        prediction = rf_model.predict(df)[0]
        pred_native = int(prediction) 
        
        # 2. Dự đoán xác suất: Kết quả là numpy.ndarray -> Cần chuyển về list()
        probability = rf_model.predict_proba(df)[0]
        prob_native = probability.tolist() 
        
        # Trả về các biến Python native
        return jsonify({
            "pred": pred_native,
            "prob": prob_native[1]
        })
    except rqs.exceptions.RequestException as e:
        print(f"Lỗi: {e}")

@app.route('/api/predict/knn', methods=['POST'])
def knn_predict():
    try:
        data = request.json
        df = pd.DataFrame([data])
        df = encoding(df)
        print(df)
        model = joblib.load('./model/knn.pkl')
        rf_model = model['model']
        if not rf_model:
            return
        # 1. Dự đoán class: Kết quả là numpy.int64 -> Cần ép về int()
        prediction = rf_model.predict(df)[0]
        pred_native = int(prediction) 
        
        # 2. Dự đoán xác suất: Kết quả là numpy.ndarray -> Cần chuyển về list()
        probability = rf_model.predict_proba(df)[0]
        prob_native = probability.tolist() 
        
        # Trả về các biến Python native
        return jsonify({
            "pred": pred_native,
            "prob": prob_native[1]
        })
    except rqs.exceptions.RequestException as e:
        print(f"Lỗi: {e}")

@app.route('/api/predict/xgboost', methods=['POST'])
def xg_predict():
    try:
        data = request.json
        df = pd.DataFrame([data])
        df = encoding(df)
        print(df)
        model = joblib.load('./model/xgboost.pkl')
        rf_model = model['model']
        if not rf_model:
            return
        # 1. Dự đoán class: Kết quả là numpy.int64 -> Cần ép về int()
        prediction = rf_model.predict(df)[0]
        pred_native = int(prediction) 
        
        # 2. Dự đoán xác suất: Kết quả là numpy.ndarray -> Cần chuyển về list()
        probability = rf_model.predict_proba(df)[0]
        prob_native = probability.tolist() 
        
        # Trả về các biến Python native
        return jsonify({
            "pred": pred_native,
            "prob": prob_native[1]
        })
    except rqs.exceptions.RequestException as e:
        print(f"Lỗi: {e}")

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    meta_list = []
    # Đảm bảo folder_path đã được define chính xác trước đó
    pkl_files = glob.glob(os.path.join(folder_path, '*.pkl'))
    
    for file_path in pkl_files:
        print(f"Đang xử lý file: {file_path}")
        
        try:
            # Load toàn bộ object (giả định format là dict: {'model': ..., 'meta': ...})
            saved_object = joblib.load(file_path)
            
            # Kiểm tra xem key 'meta' có tồn tại không để tránh KeyError
            if 'meta' not in saved_object:
                print(f"-> Bỏ qua {file_path}: Không tìm thấy key 'meta'")
                continue

            # Lấy metadata gốc
            metadata = saved_object['meta']
            metrics = metadata.get('metrics', {}) # Dùng .get() để an toàn nếu metrics null
            
            # Flatten metrics ra ngoài (nếu cần hiển thị phẳng trên bảng)
            # Dùng .get() để tránh lỗi nếu model nào đó thiếu metric
            metadata['accuracy'] = metrics.get('accuracy', None)
            metadata['f1_score'] = metrics.get('f1_score', None)
            metadata['recall']   = metrics.get('recall', None)
            metadata['precision']= metrics.get('precision', None)
            
            # QUAN TRỌNG: Thêm tên file để Client biết metadata này của file nào
            metadata['filename'] = os.path.basename(file_path)
            
            # Thêm vào danh sách kết quả
            meta_list.append(metadata)
            
            print("-> Load thành công!")
            
        except Exception as e:
            # Log lỗi nhưng không dừng API, vẫn trả về các file load được
            print(f"-> Lỗi khi load file {file_path}: {e}")

    # Trả về JSON list
    return jsonify(meta_list), 200

if __name__ == "__main__":
    app.run(debug=False, port=5001)

