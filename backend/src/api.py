import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from functools import wraps
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from sqlalchemy.exc import DatabaseError

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


# ------------------------------------------------------------------------
#  returns an array of drinks with long form representation of Drink model
# ------------------------------------------------------------------------
def get_drink_longs(drinks):

    drink_list = []

    for dr in drinks:
        drink_list.append(dr.long())

    return drink_list


# ------------------------------------------------------------------------
#  returns an array of drinks with short form representation of Drink model
# ------------------------------------------------------------------------
def get_drink_shorts(drinks):

    drink_list = []

    for dr in drinks:
        drink_list.append(dr.short())
    return drink_list


def fix_recipe_quotes(recipe):
    recipe_str = str(recipe)
    return recipe_str.replace("\'", "\"")


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():

    try:
        drinks = Drink.query.all()
    except DatabaseError:
        print("Could not get drinks from the database")
        abort(422)

    drink_shorts = get_drink_shorts(drinks)
    return jsonify({'success': True,
                    'drinks': drink_shorts}), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(f):
    try:
        drinks = Drink.query.all()
    except DatabaseError:
        print("Could not get long drinks from the database")
        abort(422)

    drink_longs = get_drink_longs(drinks)
    return jsonify({'success': True,
                    'drinks': drink_longs}), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(f):

    if not request.json:
        abort(400)

    title = request.get_json()['title']
    recipe = request.get_json()['recipe']

    if title is None or recipe is None:
        abort(400)

    # print ("title ", title)
    # print ("recipe ", recipe)

    # print ("parts ", recipe[0]['parts'])
    # print ("color", recipe[0]['color'])

    new_drink = Drink(title=title, recipe=fix_recipe_quotes(recipe))

    try:
        new_drink.insert()
    except DatabaseError:
        abort(422)

    try:
        drink_just_inserted = Drink.query.filter_by(title=title).one_or_none()
    except DatabaseError:
        abort(422)

    return jsonify({"success": True,
                    "drinks": [{"id": drink_just_inserted.id,
                                "title": title, "recipe": recipe}]}), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(f, id):
    title = ''
    recipe = ''
    if 'title' in request.get_json():
        title = request.get_json()['title']
    if 'recipe' in request.get_json():
        recipe = request.get_json()['recipe']

    if title is None and recipe is None:
        abort(400)

    # get the drink
    the_drink = Drink.query.filter_by(id=id).one_or_none()
    if the_drink is None:
        abort(404)

    if title is not None:
        the_drink.title = title
    if recipe is not None:
        the_drink.recipe = recipe

    # print ("updating drink title is ", title)

    # recipe_str = str(recipe)
    # recipe_dquot = recipe_str.replace("\'", "\"")
    # recipe_dquot = fix_recipe_quotes(recipe)
    the_drink.recipe = fix_recipe_quotes(recipe)

    try:
        the_drink.update()
    except DatabaseError:
        print("Could not update the drink")
        abort(422)


    return jsonify({"success": True,
                    "drinks": [{"id": id,
                                "title": title,
                                "recipe": recipe}]}), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(f, id):

    # get the drink
    the_drink = Drink.query.filter_by(id=id).one_or_none()
    if the_drink is None:
        abort(404)

    try:
        the_drink.delete()
    except DatabaseError:
        print("Error occurred while trying to delete the drink")
        abort(422)

    return jsonify({"success": True, "delete": id}), 200


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(403)
def resource_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 403,
                    "message": "Unauthorized"
                    }), 403


@app.errorhandler(400)
def cannot_process(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def cannot_process(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Authorization failed"
    }), 401
