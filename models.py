from datetime import datetime
from flask import Blueprint, app
from flask_sqlalchemy import SQLAlchemy


import sentry_sdk
# from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine('postgresql://postgres:238956@localhost:5432/postgres')
bp=Blueprint('model',__name__)
db = SQLAlchemy()

class Timestamp(object):
    created_date = db.Column(db.Date, default=datetime.now())
    created_time = db.Column(db.TIME, default=datetime.now())
    updated_date = db.Column(db.Date, default=datetime.now(), onupdate=datetime.now())
    updated_time = db.Column(db.TIME, default=datetime.now(), onupdate=datetime.now())

class aws_Audit_log(db.Model,Timestamp):
    __tablename__ = "audit_log"
    id = db.Column(db.Integer, primary_key=True)
    serviceName = db.Column(db.String(255), nullable=False)
    function_name = db.Column(db.String(255), nullable=False)
    # description = db.Column(db.String(255), unique=True, nullable=False)
    response = db.Column(db.JSON, nullable=True)


  
class database:
    def add_record(service_name,function_name,response):
        try:
            session = db.Session()
            add = aws_Audit_log(serviceName=service_name,function_name=function_name,response=response)
            session.add(add)
            session.commit()
            session.close()
        except Exception as e:
            print(f"An error occurred: {e}")
            sentry_sdk.capture_exception(e)
            return str(e)
        
    # def update_record(record_id,new_data):
    #     try:
    #         session = Session()
    #         update = session.query(aws_Audit_log).filter_by(id=record_id).first()
    #         if update:
    #             for key, value in new_data.items():
    #                 setattr(update, key, value)
    #             session.commit()
    #             print("Record updated successfully")
    #         else:
    #             print("Record not found")
    #         session.close()
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #         sentry_sdk.capture_exception(e)
    #         return str(e)

def create_db():
    db.create_all()