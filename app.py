from flask import Flask, jsonify
from models import bp,db
from utils.s3 import s3_bp
from celery import Celery
from tasks import tasks_bp


app=Flask(__name__)
# celery = Celery(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:first@localhost:5432/postgres'
app.config['REDIS_BROKER_URL'] = f'redis://:JUSTWIN12@localhost:6379/0'
app.config['REDIS_BACKEND_URL'] = f'db+postgresql://postgres:238956@localhost:5432/postgres'

celery = Celery(__name__,backend = app.config['REDIS_BACKEND_URL'],broker =app.config['REDIS_BROKER_URL'])

db.init_app(app)

app.register_blueprint(bp)
app.register_blueprint(s3_bp)
app.register_blueprint(tasks_bp)


@app.route("/")
def hello():
    return "Basic app"



app.run(debug=True)