from flask import Flask, jsonify
from models import bp,db
from utils.s3 import s3_bp
from celery import Celery
from tasks import tasks_bp


app=Flask(__name__)
# celery = Celery(__name__)

def create_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:first@localhost:5432/postgres' 
    db.init_app(app)

celery = Celery(__name__,backend = app.config['REDIS_BACKEND_URL'],broker =app.config['REDIS_BROKER_URL'])

# Blueprint
app.register_blueprint(bp)
app.register_blueprint(s3_bp)
app.register_blueprint(tasks_bp)


@app.route("/")
def hello():
    return "Basic app"



app.run(debug=True)