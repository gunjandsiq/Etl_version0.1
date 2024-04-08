from flask import Flask, jsonify # type: ignore
from models import bp,db
from utils.s3 import s3_bp
from etl import etl_bp
from celery import Celery # type: ignore
from config import user,password,host,port,redis_password,redis_host,redis_port,database

app=Flask(__name__)


# app.config['REDIS_BACKEND_URL'] = 'redis://:JUSTWIN12@localhost:6379/0'
# app.config['REDIS_BROKER_URL'] = 'db+postgresql://postgres:first@localhost:5432/postgres' 
celery = Celery(__name__, backend= f'db+postgresql://{user}:{password}@{host}:{port}/{database}', broker=f'redis://:{redis_password}@{redis_host}:{redis_port}/0')

def create_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{host}:{port}/{database}'
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


