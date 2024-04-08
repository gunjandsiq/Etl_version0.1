from flask import Blueprint, jsonify # type: ignore
from models import create_db
from celery import group, chain
from utils.s3 import S3Helper
# from flask_sqlalchemy import SQLAlchemy,db
from tasks import add , mul

api_bp=Blueprint('view',__name__)  

@api_bp.route("/")
def hello():
    return "Basic app"

@api_bp.route("/run-task")
def run_task():
    result = mul.delay(3, 5)
    return jsonify(result.id)

@api_bp.route('/dbcreate')
def db_create():
    create_db()
    return "All Database creatred"

@api_bp.route("/group-task")
def group_task():
    result = group([add(2,4),add(4,6),add(4,5)])
    return result

@api_bp.route("/chain-task")
def chain_task():
    result = (add.s(4, 4),mul.s(8))
    res = chain(result)
    return jsonify(res.id)

@api_bp.route("/list")
def list_bucket():
    obj = S3Helper()
    out = obj.bucket_list_names()
    return out
