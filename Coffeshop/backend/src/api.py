import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

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
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)
    short_drinks = [drink.short() for drink in drinks]
    return jsonify({'success':True,
                    'drinks':short_drinks})

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail():
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)
    long_drinks = [drink.long() for drink in drinks] 
    return jsonify({'success':True,
                    'drinks':long_drinks})

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['POST'])
@requires_auth(permission='post:drinks')
def post_drinks():    
    try:
        req_title = request.json['title']
        req_recipe = request.json['recipe']       
    except:
        abort(400)
    s_req_recipe = str(req_recipe).replace("'",'"')
    try:
        drink = Drink(title=req_title, recipe=s_req_recipe)
        drink.insert()
    except:
        abort(422)
    drinks = [drink.long()]
    return jsonify({"success": True, "drinks": drinks})

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
@app.route('/drinks/<int:drink_id>', methods = ['PATCH'])
@requires_auth(permission='patch:drinks')
def patch_drinks(drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    req_title = request.json.get('title', None)
    req_recipe = request.json.get('recipe', None)
    if req_recipe is None and req_title is None:
        abort(400)
    if req_recipe is not None:
        s_req_recipe = str(req_recipe).replace("'",'"')
    drink.title = req_title if req_title is not None else drink.title
    drink.recipe = s_req_recipe if req_recipe is not None else drink.recipe
    try:
        drink.update()
    except:
        abort(422)
    drinks = [drink.long()]
    return jsonify({"success": True, "drinks": drinks})

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
@app.route('/drinks/<int:drink_id>', methods = ['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drinks(drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({"success": True, "delete": drink_id})
    except:
        abort(422)


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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(400)
def client_error(error):
    return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
            }), 400

@app.errorhandler(401)
def auth_error(error):
    return jsonify({
            "success": False,
            "error": 401,
            "message": "Bad Request"
            }), 401

@app.errorhandler(403)
def auth_error(error):
    return jsonify({
            "success": False,
            "error": 401,
            "message": "Bad Request"
            }), 401