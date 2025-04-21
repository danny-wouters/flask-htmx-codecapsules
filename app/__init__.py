from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

persistent_path = os.getenv("PERSISTENT_STORAGE_DIR", os.path.dirname(os.path.realpath(__file__)))

app = Flask(__name__)

db_path = os.path.join(persistent_path, "sqlite.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()

# import the models after declaring the database object so that their respective tables are included in the database when it's created.
# source: https://codecapsules.io/tutorial/building-a-full-stack-application-with-flask-and-htmx/
from app import views
from app import models

db.init_app(app)

with app.app_context():
    db.create_all()
