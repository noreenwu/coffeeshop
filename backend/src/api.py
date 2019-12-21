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
#db_drop_and_create_all()
# newDrink = Drink('Root Beer Float', '[{"color":"#cfcfcf", "name":"Icecream", "parts": 1}, {"color":"#59291a", "name":"Root Beer", "parts": 3}]')
# db.session.add(newDrink)
# db.session.commit()


# def check_permissions(permission, payload):
#     if 'permissions' not in payload:
#                         raise AuthError({
#                             'code': 'invalid_claims',
#                             'description': 'Permissions not included in JWT.'
#                         }, 400)

#     if permission not in payload['permissions']:
#         raise AuthError({
#             'code': 'unauthorized',
#             'description': 'Permission not found.'
#         }, 403)
#     return True




# def requires_auth(f):
#     @wraps(f)
#     def wrapper(*args, **kwargs):
#         token = get_token_auth_header()
#         try:
#             payload = verify_decode_jwt(token)
#         except:
#             abort(401)
#         return f(payload, *args, **kwargs)

#     return wrapper


# class mydict(dict):
#     def __str__(self):
#         return json.dumps(self)

def get_drink_longs(drinks):

    drink_list = []

    for dr in drinks:
        # drink_list.append(dr.format())
        drink_list.append(dr.long())

    return drink_list

def get_drink_shorts(drinks):

    drink_list = []

    for dr in drinks:
        # drink_list.append({ dr.id: { 'title' : dr.title,
        #                              'recipe' : dr.recipe } })
        drink_list.append(dr.short())
    return drink_list


def fix_recipe_quotes(recipe):
    recipe_str = str(recipe)
    return recipe_str.replace("\'", "\"")


## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
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
    return jsonify ({ 'success': True,
                      'drinks': drink_shorts})


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
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
                    'drinks': drink_longs})


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
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

    print ("title ", title)
    print ("recipe ", recipe)

    # r = json.loads(recipe)
    print ("parts ", recipe[0]['parts'])
    print ("color", recipe[0]['color'])
    # recipe_str = str(recipe)
    # recipe_dquot = recipe_str.replace("\'", "\"")
    # print ("recipe is ", recipe_dquot)

    new_drink = Drink(title=title, recipe=fix_recipe_quotes(recipe))

    try:
        new_drink.insert()
    except DatabaseError:
        abort(422)

    try:
        drink_just_inserted = Drink.query.filter_by(title=title).one_or_none()
    except DatabaseError:
        abort(422)

    return jsonify({"success": True, "drinks": [{ "id": drink_just_inserted.id, "title": title, "recipe": recipe}] }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
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

    print ("updating drink title is ", title)

    # recipe_str = str(recipe)
    # recipe_dquot = recipe_str.replace("\'", "\"")
    # recipe_dquot = fix_recipe_quotes(recipe)
    the_drink.recipe = fix_recipe_quotes(recipe)
    print ("   and recipe is ", recipe_dquot)
    try:
        the_drink.update()
    except:
        print("Could not update the drink")
        abort(422)

    return jsonify({"success": True}), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
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
        print("an error occurred while trying to delete the drink")
        abort(422)

    return jsonify({"success": True, "delete": id}), 200


## Error Handling
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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


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