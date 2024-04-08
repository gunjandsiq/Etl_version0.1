from flask import Flask, jsonify # type: ignore
from models import bp,db
from utils.s3 import s3_bp
from etl import etl_bp
from celery import Celery # type: ignore


app=Flask(__name__)


# app.config['REDIS_BACKEND_URL'] = 'redis://:JUSTWIN12@localhost:6379/0'
# app.config['REDIS_BROKER_URL'] = 'db+postgresql://postgres:first@localhost:5432/postgres' 
celery = Celery(__name__, backend= 'db+postgresql://postgres:238956@localhost:5432/postgres', broker='redis://:JUSTWIN12@localhost:6379/0')

def create_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:238956@localhost:5432/postgres'
    db.init_app(app)
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Kolkata',
        worker_disable_rate_limits = False,
        result_extended=True,
        enable_utc=True,
        broker_connection_retry_on_startup=True,
    )
   
    # Blueprint
    app.register_blueprint(bp)
    app.register_blueprint(s3_bp)
    app.register_blueprint(etl_bp)
    from views import api_bp
    app.register_blueprint(api_bp)
    
    return app 


