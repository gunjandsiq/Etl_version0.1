import psycopg2
# from sqlalchemy import func, BigInteger, Integer, Boolean, String, Float, DateTime, Date, Column, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Timestamp(object):
    created_date = db.Column(db.Date, default=datetime.now())
    created_time = db.Column(db.TIME, default=datetime.now())
    updated_date = db.Column(db.Date, default=datetime.now(), onupdate=datetime.now())
    updated_time = db.Column(db.TIME, default=datetime.now(), onupdate=datetime.now())
    created_by = db.Column(db.String, default='app')
    updated_by = db.Column(db.String, default='app')

class Iaas(db.Model,Timestamp):
    __tablename__ = "iaas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)

class Service(db.Model,Timestamp):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    iaas_id = db.Column(db.Integer, db.ForeignKey('iaas.id'))

class Service_Type(db.Model,Timestamp):
    __tablename__ = "service_type"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255), unique=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))

class Pricing(db.Model,Timestamp):
    __tablename__ = "pricing"
    id = db.Column(db.Integer,primary_key=True)
    # service_type = db.Column(db.String(255),nullable=False)
    type = db.Column(db.String(225))
    price = db.Column(db.Float,nullable=False)
    region = db.Column(db.String(255),nullable=False)
    currency = db.Column(db.String(255),nullable=False)
    memory = db.Column(db.String(255),nullable=False)
    operating_system =db.Column(db.String(255))
    vcpu = db.Column(db.Integer)
    service_type_id = db.Column(db.Integer,db.ForeignKey("service_type.id"))

class Retailer(db.Model,Timestamp):
    __tablename__ = "retailer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class Scraper_service(db.Model,Timestamp):
    __tablename__ = "scraper_service"
    id = db.Column(db.Integer, primary_key=True)
    success_rate = db.Column(db.String(255))
    item_count = db.Column(db.Integer)
    country = db.Column(db.String(255))
    version = db.Column(db.String(255))
    pricing_id = db.Column(db.Integer,db.ForeignKey("pricing.id")) 
    retailer_id = db.Column(db.Integer,db.ForeignKey("retailer.id"))

class Product(db.Model,Timestamp):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    price = db.Column(db.Float,nullable=False)
    seller_name = db.Column(db.String(255))
    ratings = db.Column(db.String(255))
    variations = db.Column(db.String(255))
    description = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    retailer_id = db.Column(db.Integer,db.ForeignKey("retailer.id"))

class Review(db.Model,Timestamp):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(255))
    source = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))

class Listing(db.Model,Timestamp):
    __tablename__ = "listing"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255))
    price = db.Column(db.Float,nullable=False)
    sponsored = db.Column(db.Boolean, nullable=False)
    best_seller = db.Column(db.Boolean, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))

def createdb():
    db.create_all()
