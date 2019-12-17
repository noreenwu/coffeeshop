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


def check_permissions(permission, payload):
    if 'permissions' not in payload:
                        raise AuthError({
                            'code': 'invalid_claims',
                            'description': 'Permissions not included in JWT.'
                        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        print ("authorization header missing")
        abort(401)
        # raise AuthError({
        #     'code': 'authorization_header_missing',
        #     'description': 'Authorization header is expected.'
        # }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        print ("authorization header must start with Bearer")
        abort(401)
        # raise AuthError({
        #     'code': 'invalid_header',
        #     'description': 'Authorization header must start with "Bearer".'
        # }, 401)

    elif len(parts) == 1:
        print ("Token not found")
        abort(401)
        # raise AuthError({
        #     'code': 'invalid_header',
        #     'description': 'Token not found.'
        # }, 401)

    elif len(parts) > 2:
        print ("Invalid header: authorization header must be bearer token")
        abort(401)
        # raise AuthError({
        #     'code': 'invalid_header',
        #     'description': 'Authorization header must be bearer token.'
        # }, 401)

    token = parts[1]
    return token

def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = get_token_auth_header()
        try:
            payload = verify_decode_jwt(token)
        except:
            abort(401)
        return f(payload, *args, **kwargs)

    return wrapper

def get_drink_shorts(drinks):

    drink_list = []

    for dr in drinks:
        drink_list.append({ dr.id: { 'title' : dr.title,
                                     'recipe' : dr.recipe } })

    return drink_list


## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():

    try:
        drinks = Drink.query.all()
    except DatabaseError:
        print("Could not get drinks from the database")
        abort(422)

    if len(drinks) > 0:
        drink_shorts = get_drink_shorts(drinks)
        return jsonify ({ 'drinks': drink_shorts})        
    else:
        print ("empty list of drinks")
        return jsonify ({ 'success': True,
                          'drinks': []
                        })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth
def get_drinks_detail():
    return jsonify ({ 'drinks-detail': 'detail'})


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
@requires_auth
def add_drink():
    return jsonify({"success": True}), 200

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
@requires_auth
def update_drink():
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
@requires_auth
def delete_drink():
    return jsonify({"success": True}), 200


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