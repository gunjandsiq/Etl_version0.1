from datetime import datetime
from sqlalchemy import create_engine, event, Date, TIME, JSON, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import sentry_sdk
# from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://postgres:238956@localhost:5432/postgres')
Session = sessionmaker(bind=engine)
Base =  declarative_base()

class Timestamp(object):
    created_date = Column(Date, default=datetime.now())
    created_time = Column(TIME, default=datetime.now())
    updated_date = Column(Date, default=datetime.now(), onupdate=datetime.now())
    updated_time = Column(TIME, default=datetime.now(), onupdate=datetime.now())

class aws_Audit_log(Base,Timestamp):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    serviceName = Column(String(255), nullable=False)
    function_name = Column(String(255), nullable=False)
    # description = db.Column(db.String(255), unique=True, nullable=False)
    response = Column(JSON, nullable=True)

Base.metadata.create_all(engine)

class database:
    def add_record(service_name,function_name,response):
        try:
            session = Session()
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