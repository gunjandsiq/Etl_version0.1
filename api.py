from flask import Blueprint, jsonify # type: ignore
from models import create_db
# from flask_sqlalchemy import SQLAlchemy,db
from tasks import add

api_bp=Blueprint('view',__name__)  

@api_bp.route("/")
def hello():
    return "Basic app"

@api_bp.route("/run_task")
def run_task():
    result = add.delay(3, 5)
    return jsonify(result.id)

@api_bp.route('/dbcreate')
def db_create():
    create_db()
    return "All Database creatred"

