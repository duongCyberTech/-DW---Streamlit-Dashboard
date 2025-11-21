from flask_restful import Resource, reqparse
from flask import jsonify, request
from app import db
from app.models import Retail, Rfm 
import pandas as pd
from sqlalchemy import func, desc 

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
        args = retail_parser.parse_args()
        retail = Retail(**args)
        db.session.add(retail)
        db.session.commit()
        return jsonify(retail.to_dict())


class StatsResource(Resource):
    def get(self):
        stat_type = request.args.get('mode', 'all', type=str)

        if stat_type == "all":
            total_records = Retail.query.count()

            total_revenue = db.session.query(db.func.sum(Retail.totalamount)).scalar() or 0
            avg_price = db.session.query(db.func.avg(Retail.price)).scalar() or 0
            all_year = db.session.query(Retail.year).all()

            return jsonify({
                "total_records": total_records,
                "total_revenue": round(float(total_revenue), 2),
                "avg_price": round(float(avg_price), 2),
                "years": sorted(list(set([item.year for item in all_year])))
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
        year = request.args.get('year', type=int)
        revenue_monthly = (
            Retail.query.filter_by(year=year).all()  # trả về list
        )

        res = [item.to_dict() for item in revenue_monthly]
        df = pd.DataFrame(res)
        revenue_by_month = df.groupby('month')['totalamount'].sum().reset_index()
        revenue_by_month = revenue_by_month.sort_values(by='month',ascending=True).to_dict()

        revenue_cat = Retail.query.with_entities(Retail.category, Retail.totalamount).filter_by(year=year).all()
        df = pd.DataFrame(revenue_cat)
        revenue_cat = df.groupby('category')['totalamount'].sum().reset_index()
        revenue_cat = revenue_cat.sort_values(by='totalamount', ascending=False).to_dict()

        return jsonify({
            "revenue_monthly": revenue_by_month, 
            "revenue_cat": revenue_cat
        })
    
class RfmAnalysis(Resource):
    def get(self):
        limit = request.args.get('limit', 50, type=int)
        rfm_data = Rfm.query.with_entities(Rfm.customer_id, Rfm.recency, Rfm.freq, Rfm.monetary)
        df = pd.DataFrame(rfm_data)
        rfm_data = df.sort_values(by=['recency', 'freq', 'monetary'], ascending=False)\
            .head(limit)\
            .to_dict(orient='records')
        return jsonify({"rfm_data": rfm_data})
