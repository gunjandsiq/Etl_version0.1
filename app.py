from flask import Flask
from models import bp,db
from utils.s3 import s3_bp



app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:238956@localhost:5432/postgres'

db.init_app(app)

app.register_blueprint(bp)
app.register_blueprint(s3_bp)


@app.route("/")
def hello():
    return "Basic app"

app.run(debug=True)