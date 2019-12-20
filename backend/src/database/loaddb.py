import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer

from flask import Flask, request, jsonify, abort
# from sqlalchemy import exc
import json
# from functools import wraps
# from flask_cors import CORS
# from models import db_drop_and_create_all, setup_db, Drink

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()
app = Flask(__name__)

def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


class Drink(db.Model):
    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Title
    title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe =  Column(String(180), nullable=False)    

    def short(self):
        print(json.loads(self.recipe))
        short_recipe = [{'color': r['color'], 'parts': r['parts']} for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    def long(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()

setup_db(app)

drinks = Drink.query.all()

for dr in drinks:
    dr.delete()
    

newDrink1 = Drink(title='Seattle Root Beer Float II', 
                 recipe='[{"color":"#cfcfcf", "name":"Icecream", "parts": 1}, {"color":"#59291a", "name":"Root Beer", "parts": 3}]')

db.session.add(newDrink1)
db.session.commit()


newDrink2 = Drink(title='Lemonade I', 
                  recipe='[{"color":"yellow", "name":"lemon juice", "parts": 1}, {"color":"blue", "name":"water", "parts": 3}]')

db.session.add(newDrink2)
db.session.commit()