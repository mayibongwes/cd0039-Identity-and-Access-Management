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
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
@app.route('/drinks')
@requires_auth('get:drinks')
def get_drinks(jwt):
    drinks = []
    for drink in Drink.query.filter().all():
        drinks = drink.long()
    return jsonify({"success": True, "drinks": drinks}), 200

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = []
    for drink in Drink.query.filter().all():
        drinks.append(drink.longg())
    return jsonify({"success": True, "drinks": drinks}), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
    drinks = []
    body = request.get_json()
    try:
        title = body['title']
        
        recipe = json.dumps(body["recipe"])

        # There is a bug when a recipe has only 1 ingredient the datatype is saved differently which then affects then
        if recipe[0] == "{":
            recipe = "[" + recipe + "]"

        print(recipe)
        drink  = Drink(title=title, recipe=recipe)
        drink.insert()
        drinks.append(drink.long())
    except Exception as e:
        print('Error: ' + str(e))
        abort(403)

    

    return jsonify({"success": True, "drinks": drinks}), 201

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt,drink_id):
    drinks = []
    body = request.get_json()
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        title  = body.get("title", None)
        recipe = json.dumps(body.get("recipe", None))

        if title is not None:
            drink.title = title
        if recipe is not None:
            drink.recipe = recipe
        
        drink.update()
        drinks.append(drink.long())
    except Exception as e:
        print('Error: ' + str(e))
        abort(403)

    return jsonify({"success": True, "drinks": drinks}), 200

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('patch:drinks')
def delete_drink(jwt,drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
    
        drink.delete()
    except Exception as e:
        print('Error: ' + str(e))
        abort(400)

    return jsonify({"success": True, "delete": drink_id}), 204

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


@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401

@app.errorhandler(403)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403

@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 4001
