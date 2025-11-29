from flask_restful import Resource, reqparse
from flask import jsonify, request
import uuid6
from app import db
from app.models import Retail, Rfm 
import pandas as pd
from sqlalchemy import func, desc 
import calendar
import json
from .utils.quantile_segment import RFMAnalyzer
from .utils.generate_id import generate_uuid7
from .utils.time import time_convert
# Define the parser for POST request
retail_parser = reqparse.RequestParser()
retail_parser.add_argument('invoice_no', type=str, required=True)
retail_parser.add_argument('quantity', type=int, required=True)
retail_parser.add_argument('price', type=float, required=True)
retail_parser.add_argument('totalamount', type=float, required=True)
retail_parser.add_argument('customer_id', type=str)
retail_parser.add_argument('gender', type=str)
retail_parser.add_argument('age', type=int)
retail_parser.add_argument('payment_method', type=str)
retail_parser.add_argument('invoice_date', type=str)
retail_parser.add_argument('day', type=int)
retail_parser.add_argument('month', type=int)
retail_parser.add_argument('quarter', type=int)
retail_parser.add_argument('year', type=int)
retail_parser.add_argument('category', type=str)
retail_parser.add_argument('shopping_mall', type=str)

class RetailListResource(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = (
            Retail.query
            .order_by(Retail.invoice_no)
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return jsonify({
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "data": [item.to_dict() for item in pagination.items]
        })

    def post(self):
        data = request.get_json()
        if not data:
            return {"message": "Payload không được cung cấp hoặc không phải JSON."}, 400
        customer_id = data.get('customer_id')
        gender = data.get('gender')
        age = data.get('age')
        transactions_json = data.get('transactions')

        if not transactions_json:
            return {"message": "Thiếu trường 'transactions' (hóa đơn mua sắm)."}, 400

        # 3. Chuyển chuỗi JSON của transactions thành DataFrame của Pandas
        try:
            transactions_list = json.loads(transactions_json)
            df_transactions = pd.DataFrame(transactions_list)
            
        except Exception as e:
            return {"message": f"Lỗi khi xử lý dữ liệu giao dịch: {e}"}, 400
        
        df_post = df_transactions
        df_post['age'] = age
        df_post['gender'] = gender
        df_post['customer_id'] = customer_id
        if 'invoice_no' not in df_post.columns:
            print("Cột 'invoice_no' chưa tồn tại. Đang tạo...")
            df_post['invoice_no'] = df_post['gender'].apply(generate_uuid7)
        else:
            print("Cột 'invoice_no' đã tồn tại. Không cần tạo mới.")
        
        df_post[['day', 'month', 'year', 'quarter']] = df_post['invoice_date'].apply(time_convert)
        df_post['invoice_date'] = pd.to_datetime(df_post['invoice_date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
        df_post['totalamount'] = df_post['quantity'].astype(int) * df_post['price'].astype(float) # Thêm cột totalamount
        # Chuyển đổi thành list of dict
        transactions_to_save = df_post.to_dict(orient='records')
        # Tạo list chứa các đối tượng Retail
        retail_objects = []
        for transaction_data in transactions_to_save:
        # Chuyển dict thành đối tượng Retail
            retail_item = Retail(**transaction_data) 
            retail_objects.append(retail_item)
        db.session.add_all(retail_objects)
        df_update_rfm = pd.DataFrame(transactions_to_save)

        latest_index = df_update_rfm['invoice_date'].idxmax()
        latest_record = df_update_rfm.loc[latest_index]
        end_period = latest_record['invoice_date']
        end_period = pd.to_datetime(end_period)
        start_period = end_period - pd.DateOffset(years=2)

        new_freq = Retail.query.filter(
            Retail.invoice_date >= start_period,
            Retail.invoice_date <= end_period,
            Retail.customer_id == customer_id # Quan trọng: Phải lọc theo customer_id
        ).count()

        new_monetary = db.session.query(
            func.avg(Retail.totalamount)
        ).filter(
            Retail.invoice_date >= start_period,
            Retail.invoice_date <= end_period,
            Retail.customer_id == customer_id # Quan trọng: Phải lọc theo customer_id
        ).scalar()

        last_rfm = Rfm.query.with_entities(Rfm.recency, Rfm.invoice_date).filter_by(customer_id=customer_id).all()
        last_rfm = last_rfm[0]

        l_recency = last_rfm.recency if last_rfm else 9999
        l_invoice_date = last_rfm.invoice_date if last_rfm else None

        # Tính toán chênh lệch ngày giữa hóa đơn mới nhất và hóa đơn cũ nhất
        if l_invoice_date:
            l_invoice_date_ts = pd.to_datetime(l_invoice_date)
            diff = (end_period - l_invoice_date_ts).days # Đã sửa lỗi Timedelta .dt
            # Công thức Recency mới: Độ mới cũ - Khoảng cách ngày đã trôi qua
            new_recency = l_recency - diff 
        else:
            # Nếu là giao dịch đầu tiên, recency = 0 (hoặc khoảng cách ngày từ end_period đến hôm nay nếu cần)
            new_recency = 0

        totalamount = float(latest_record['quantity']) * float(latest_record['price'])
        rfm_data = {
            # Ép kiểu rõ ràng các giá trị từ Series (là kiểu NumPy) sang Python chuẩn
            'invoice_no': str(latest_record['invoice_no']),
            'quantity': int(latest_record['quantity']),
            'price': float(latest_record['price']),
            
            # Ép kiểu Total Amount sang float
            # Sử dụng giá trị totalamount đã được tính toán (hoặc tính lại và ép kiểu float)
            'totalamount': float(totalamount), 
            
            'customer_id': str(customer_id), # Đảm bảo là string
            'gender': str(gender),
            'age': int(age),
            'payment_method': str(latest_record['payment_method']),
            
            # Ép kiểu cho các trường ngày tháng đơn lẻ
            'day': int(latest_record['day']),
            'month': int(latest_record['month']),
            'quarter': int(latest_record['quarter']),
            'year': int(latest_record['year']),
            
            'category': str(latest_record['category']),
            'shopping_mall': str(latest_record['shopping_mall']),

            # Các giá trị RFM đã tính toán
            'invoice_date': end_period.strftime('%Y-%m-%d'), 
            'recency': int(new_recency),
            'freq': int(new_freq),
            'monetary': float(new_monetary) if new_monetary is not None else 0.0
        }
        rfm_item = Rfm(**rfm_data)
        db.session.add(rfm_item)
        db.session.commit()
        return jsonify(rfm_item.to_dict())

class StatsResource(Resource):
    def get(self):
        stat_type = request.args.get('mode', 'all', type=str)

        if stat_type == "all":
            total_records = Retail.query.count()

            total_revenue = db.session.query(db.func.sum(Retail.totalamount)).scalar() or 0
            avg_price = db.session.query(db.func.avg(Retail.price)).scalar() or 0
            all_year = db.session.query(Retail.year).all()
            all_cate_by_mall = db.session.query(Retail.shopping_mall, Retail.category).distinct().all()
            all_payment = db.session.query(Retail.payment_method).distinct().all()
            return jsonify({
                "total_records": total_records,
                "total_revenue": round(float(total_revenue), 2),
                "avg_price": round(float(avg_price), 2),
                "years": sorted(list(set([item.year for item in all_year]))),
                "categories": [{
                    "mall": item.shopping_mall,
                    "category": item.category
                } for item in all_cate_by_mall],
                "payment_method": [item.payment_method for item in all_payment]
            })

        elif stat_type == "revenue":
            total_revenue = db.session.query(db.func.sum(Retail.totalamount)).scalar() or 0
            return jsonify({"total_revenue": float(total_revenue)})

        elif stat_type == "avg_price":
            avg_price = db.session.query(db.func.avg(Retail.price)).scalar() or 0
            return jsonify({"avg_price": float(avg_price)})

        else:
            return jsonify({"error": "Invalid mode"}), 400
        
class RevenueByMonthInYear(Resource):
    def get(self):
        period = request.args.get('period', type=str)
        time_value = request.args.get('time_value', type=int)
        revenue_cat = None
        if period == '7-days':
            latest_7_dates = (
                db.session.query(Retail.invoice_date)
                .distinct()
                .order_by(Retail.invoice_date.desc())
                .limit(7)
            )

            revenue = Retail.query.with_entities(
                Retail.invoice_date, 
                Retail.shopping_mall, 
                Retail.totalamount
            ).filter(
                Retail.invoice_date.in_(latest_7_dates)
            ).order_by(
                Retail.invoice_date.asc()
            ).all()

            df = pd.DataFrame(revenue)
            revenue = df.groupby(['invoice_date', 'shopping_mall'])['totalamount'].sum().reset_index()\
                        .rename(columns={'invoice_date': 'time', 'shopping_mall': 'mall', 'totalamount': 'revenue'})
            
            revenue_cat = Retail.query.with_entities(
                    Retail.category, 
                    Retail.totalamount, 
                    Retail.shopping_mall
                ).filter(
                    Retail.invoice_date.in_(latest_7_dates)
                ).order_by(
                    Retail.invoice_date.asc()
                ).all()
            df = pd.DataFrame(revenue_cat)
            revenue_cat = df.groupby(['shopping_mall', 'category'])['totalamount'].sum().reset_index()\
                            .rename(columns={'invoice_date': 'time', 'shopping_mall': 'mall', 'totalamount': 'revenue'})
            revenue_cat = revenue_cat.to_dict(orient='records')
            
        elif period == 'monthly':
            revenue = (
                Retail.query.with_entities(Retail.month, Retail.totalamount, Retail.shopping_mall).filter_by(year=time_value).all()  # trả về list
            )

            df = pd.DataFrame(revenue)
            df['month'] = df['month'].astype(int)
            if str(df['month'].dtype) != 'int64' and str(df['month'].dtype) != 'int32':
                print("Type cast failed!") # Debug
                return
            revenue = df.groupby(['month', 'shopping_mall'])['totalamount'].sum().reset_index()
            revenue = revenue.sort_values(by='month',ascending=True)
            revenue['month'] = revenue['month'].apply(lambda x: calendar.month_abbr[int(x)])
            revenue = revenue.rename(columns={'month': 'time', 'shopping_mall': 'mall', 'totalamount': 'revenue'})

            revenue_cat = Retail.query.with_entities(Retail.category, Retail.totalamount, Retail.shopping_mall).filter_by(year=time_value).all()
            df = pd.DataFrame(revenue_cat)
            revenue_cat = df.groupby(['shopping_mall', 'category'])['totalamount'].sum().reset_index()\
                            .rename(columns={'month': 'time', 'shopping_mall': 'mall', 'totalamount': 'revenue'})
            revenue_cat = revenue_cat.to_dict(orient='records')

        elif period == 'quarter':
            n_latest_year = (
                db.session.query(Retail.year)
                .distinct().order_by(Retail.year.desc())
                .limit(time_value)
            )

            revenue = Retail.query.with_entities(
                Retail.quarter, 
                Retail.year,
                Retail.shopping_mall, 
                func.sum(Retail.totalamount).label('total_revenue')
            ).filter(
                Retail.year.in_(n_latest_year)
            ).order_by(
                Retail.year.asc(),
                Retail.quarter.asc()
            ).group_by(
                Retail.year, 
                Retail.quarter,
                Retail.shopping_mall
            ).all()

            df = pd.DataFrame(revenue)
            df['time'] = 'Quý ' + df['quarter'].astype(str) + ' - Năm ' + df['year'].astype(str)
            revenue = df.drop(columns=['quarter', 'year'])
            revenue = revenue.rename(columns={'month': 'time', 'shopping_mall': 'mall', 'total_revenue': 'revenue'})
            
            revenue_cat = Retail.query.with_entities(
                Retail.category, Retail.totalamount, Retail.shopping_mall
            ).filter(
                Retail.year.in_(n_latest_year)
            ).order_by(
                Retail.year.asc(),
                Retail.quarter.asc()
            ).all()
            df = pd.DataFrame(revenue_cat)
            revenue_cat = df.groupby(['shopping_mall', 'category'])['totalamount'].sum().reset_index()\
                            .rename(columns={'month': 'time', 'shopping_mall': 'mall', 'totalamount': 'revenue'})
            revenue_cat = revenue_cat.to_dict(orient='records')
        elif period == 'annually':
            n_latest_year = (
                db.session.query(Retail.year)
                .distinct().order_by(Retail.year.desc())
                .limit(time_value)
            )

            revenue = Retail.query.with_entities(
                Retail.year,
                Retail.shopping_mall, 
                func.sum(Retail.totalamount).label('total_revenue')
            ).filter(
                Retail.year.in_(n_latest_year)
            ).order_by(
                Retail.year.asc(),
            ).group_by(
                Retail.year, 
                Retail.shopping_mall
            ).all()
            df = pd.DataFrame(revenue)
            df['time'] = df['year'].astype(str)
            revenue = df.drop(columns=['year'])\
                .rename(columns={'month': 'time', 'shopping_mall': 'mall', 'total_revenue': 'revenue'})
            
            revenue_cat = Retail.query.with_entities(
                Retail.category, Retail.totalamount, Retail.shopping_mall
            ).filter(
                Retail.year.in_(n_latest_year)
            ).order_by(
                Retail.year.asc(),
            ).all()
            df = pd.DataFrame(revenue_cat)
            revenue_cat = df.groupby(['shopping_mall', 'category'])['totalamount'].sum().reset_index()\
                            .rename(columns={'month': 'time', 'shopping_mall': 'mall', 'totalamount': 'revenue'})
            revenue_cat = revenue_cat.to_dict(orient='records')

        return jsonify({
            "revenue_by_time": revenue.to_dict(orient='records'), 
            "revenue_cat": None if revenue_cat == None else revenue_cat
        })
