from flask import Flask, jsonify
from models import bp,db
from utils.s3 import s3_bp
# from celery import Celery
from tasks import add


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:first@localhost:5432/postgres'


db.init_app(app)

app.register_blueprint(bp)
app.register_blueprint(s3_bp)


@app.route("/")
def hello():
    return "Basic app"

@app.route("/run_task")
def run_task():
    result = add.delay(3, 5) 
    return jsonify({"task_id": result.id})

app.run(debug=True)