from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from .config import Config
from .extensions import db
from .resources.retail import *
from .resources.rfm import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # init db
    db.init_app(app)

    api = Api(app)

    # Register routes
    api.add_resource(RetailListResource, '/api/retail')
    api.add_resource(StatsResource, '/api/count-transactions')
    api.add_resource(RevenueByMonthInYear, '/api/revenue-by-month')
    api.add_resource(RfmAnalysis, '/api/rfm')
    api.add_resource(RfmSegmentation, '/api/rfm-segmentation')

    with app.app_context():
        db.create_all()

    return app
