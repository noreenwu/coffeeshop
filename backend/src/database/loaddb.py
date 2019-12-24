import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer
from flask import Flask, request, jsonify, abort
import json
# from models import *


database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(
                                os.path.join(project_dir, database_filename))


db = SQLAlchemy()
app = Flask(__name__)


# --------------------------------------------------------
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


from models import *

setup_db(app)


# -------------------------------------------------------
#  delete all drinks
# -------------------------------------------------------
drinks = Drink.query.all()

for dr in drinks:
    dr.delete()


# -------------------------------------------------------
#  add 2 drinks to the database
# -------------------------------------------------------
newDrink1 = Drink(title='Seattle Root Beer Float',
                  recipe='[{"color": "#cfcfcf", "name": "Ice cream", "parts": 1 }, {"color": "#59291a","name": " Root Beer","parts": 3}]')

db.session.add(newDrink1)
db.session.commit()


newDrink2 = Drink(title='Lemonade I',
                  recipe='[{"color": "yellow", "name": "lemon juice", "parts": 1}, {"color": "blue", "name": "water", "parts": 3}]')

db.session.add(newDrink2)
db.session.commit()
