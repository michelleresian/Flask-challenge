#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)


db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes')
def get_heroes():
    heroes_dict = [heroes.serialize() for heroes in Hero.query.all()]
    response = make_response(heroes_dict, 200)
    return response
    

# UPDATE 
@app.route('/heroes/<int:id>')
def get_heroes_by_id(id):
    hero = Hero.query.filter_by(id=id).first()

    if hero == None:
        response_body = {"error": "Hero not found"}
        return make_response(response_body, 404)
    else:
        #hero_dict = hero.to_dict()
        hero_dict = hero.to_dict()
        response = make_response(hero_dict, 200)
        return response 
    
    
@app.route('/powers')
def get_powers():
    powers_dict = [powers.serialize() for powers in Power.query.all()]
    response = make_response(powers_dict, 200)
    return response


@app.route('/powers/<int:id>', methods = ['GET', 'PATCH'])
def get_powers_by_id(id):
    power = Power.query.filter_by(id=id).first()

    if power == None:
        response_body = {"error": "Power not found"}
        return make_response(response_body, 404)
    else:
        if request.method == 'GET':
            power_dict = power.serialize()
            response = make_response(power_dict, 200)
            return response 
            
        # EDIT FROM HERE 
        elif request.method == 'PATCH':
            data = request.get_json()
            if 'description' not in data or len(data['description']) < 20:
                return jsonify({"errors": ["validation errors"]}), 400

            power.description = data['description']
            db.session.commit()

            power_data = {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
            return jsonify(power_data), 200


@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    if 'hero_id' not in data or 'power_id' not in data:
        return jsonify({'error': 'hero_id and power_id are required'}), 400

    if 'strength' in data and data['strength'] not in ('Strong', 'Weak', 'Average'):
        return jsonify({'errors': ['validation errors']}), 400

    #hero = db.session.get(data['hero_id'])
    #power = db.session.get(data['power_id'])
    hero = Hero.query.filter_by(id=data['hero_id']).first()
    power = Power.query.filter_by(id=data['power_id']).first()

    if hero is None or power is None:
        return jsonify({'error': 'Hero or power not found'}), 404

    hero_power = HeroPower(
        strength=data.get('strength'),
        hero_id=data['hero_id'],
        power_id=data['power_id']
    )
    db.session.add(hero_power)
    db.session.commit()

    return jsonify({
        'id': hero_power.id,
        'hero_id': hero.id,
        'power_id': power.id,
        'strength': hero_power.strength,
        'hero': hero.name,
        'power': power.name
    }), 200



if __name__ == '__main__':
    app.run(port=5555, debug=True)