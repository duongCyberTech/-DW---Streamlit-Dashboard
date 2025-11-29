from flask_restful import Resource, reqparse
from flask import jsonify, request
from app import db
from app.models import Retail, Rfm 
import pandas as pd
from sqlalchemy import func, desc 
import calendar
from .utils.quantile_segment import RFMAnalyzer

class RfmAnalysis(Resource):
    def get(self):
        limit = request.args.get('limit', 50, type=int)
        mall = request.args.get('mall', None, type=str)
        if mall == None:
            rfm_data = Rfm.query.with_entities(Rfm.customer_id, Rfm.recency, Rfm.freq, Rfm.monetary)
        else: rfm_data = Rfm.query.with_entities(Rfm.customer_id, Rfm.recency, Rfm.freq, Rfm.monetary).filter_by(shopping_mall=mall)
        df = pd.DataFrame(rfm_data)
        rfm_data = df.sort_values(by=['recency', 'freq', 'monetary'], ascending=False)\
            .head(limit)\
            .to_dict(orient='records')
        return jsonify({"rfm_data": rfm_data})

class RfmSegmentation(Resource):
    def get(self):
        mall = request.args.get('mall', None, type=str)
        df = Rfm.query.with_entities(Rfm.customer_id, Rfm.recency, Rfm.freq, Rfm.monetary).filter_by(shopping_mall=mall)
        df = [{
            "customer_id": item.customer_id,
            "Recency": int(item.recency),
            "Frequency": int(item.freq),
            "Monetary": float(item.monetary)
        } for item in df]

        df = pd.DataFrame(df)
        analyzer = RFMAnalyzer()
        df_rfm = analyzer.process(df)
        df_rfm = analyzer.segmentation(df_rfm)

        return jsonify({"rfm": df_rfm.to_dict(orient='records')})