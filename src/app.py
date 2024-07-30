"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Faves

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Users
@app.route('/users', methods=['GET'])
def handle_users():
    users = User.query.all()
    all_users = list(map(lambda i: i.serialize(), users))

    return jsonify(all_users), 200

@app.route('/users', methods=['POST'])
def create_user():
    request_user = request.get_json()

    user = User(
        email = request_user["email"],
        password = request_user["password"]
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(request_user), 200

# Characters
@app.route('/characters', methods=['GET'])
def handle_chars():
    chars = Characters.query.all()
    all_chars = list(map(lambda i: i.serialize(), chars))

    return jsonify(all_chars), 200

@app.route('/characters', methods=['POST'])
def create_char():
    request_char = request.get_json()

    char1 = Characters(
        name = request_char["name"], 
        height = request_char["height"],
        mass = request_char["mass"],
        hair_color = request_char["hair_color"],
        skin_color = request_char["skin_color"],
        eye_color = request_char["eye_color"],
        birth_year = request_char["birth_year"],
        gender = request_char["gender"]
    )

    db.session.add(char1)
    db.session.commit()

    return "The force is with you", 200

@app.route('/characters/<int:char_id>', methods=['GET'])
def get_char(char_id):
    char = Characters.query.get(char_id)
    unique_char = char.serialize()

    return jsonify(unique_char), 200

@app.route('/characters/<int:char_id>', methods=['DELETE'])
def del_char(char_id):
    char = Characters.query.get(char_id)

    db.session.delete(char)
    db.session.commit()

    return "The force is with you", 200

# Planets
@app.route('/planets', methods=['GET'])
def handle_planets():
    planets = Planets.query.all()
    all_planets = list(map(lambda i: i.serialize(), planets))

    return jsonify(all_planets), 200

@app.route('/planets', methods=['POST'])
def create_planet():
    request_planet = request.get_json()
    planet1 = Planets(
        name = request_planet["name"], 
        rotation_period = request_planet["rotation_period"],
        orbital_period = request_planet["orbital_period"],
        diameter = request_planet["diameter"],
        climate = request_planet["climate"],
        terrain = request_planet["terrain"],
    )

    db.session.add(planet1)
    db.session.commit()

    return "The force is with you", 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get(planet_id)
    unique_planet = planet.serialize()

    return jsonify(unique_planet), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def del_planet(planet_id):
    planet = Planets.query.get(planet_id)

    db.session.delete(planet)
    db.session.commit()

    return "The force is with you", 200

# Faves
@app.route('/favorites/user/<int:user_id>', methods=['GET'])
def get_faves(user_id):
    user = User.query.get(user_id)

    fave_chars = (
       db.session.query(Faves, Characters)
       .join(Characters, Faves.fave_planet == Characters.id)
       .filter(Faves.user_id == user_id)
       .all() 
    )

    list_fave_chars = [
        {
            "id": char.id,
            "height": char.height,
            "mass": char.mass,
            "hair_color": char.hair_color,
            "skin_color": char.skin_color,
            "eye_color": char.eye_color,
            "birth_year": char.birth_year,
            "gender": char.gender
        }
        for Faves, char in fave_chars
    ]

    fave_planets = (
       db.session.query(Faves, Planets)
       .join(Planets, Faves.fave_planet == Planets.id)
       .filter(Faves.user_id == user_id)
       .all() 
    )

    list_fave_planets = [
        {
            "id": planet.id,
            "name": planet.name,
            "rotation_period": planet.rotation_period,
            "orbital_period": planet.orbital_period,
            "diameter": planet.diameter,
            "climate": planet.climate,
            "terrain": planet.terrain
        }
        for Faves, planet in fave_planets
    ]



    return jsonify(list_fave_chars + list_fave_planets), 200

# Fave Characters
@app.route('/favorites/user/<int:user_id>/characters/<int:char_id>', methods=['POST'])
def create_fave_char(user_id, char_id):
    new_fave_char = Faves(
        user_id = user_id,
        fave_char = char_id
    )

    db.session.add(new_fave_char)
    db.session.commit()

    return "The force is with you", 200

@app.route('/favorites/user/<int:user_id>/characters/<int:char_id>', methods=['DELETE'])
def del_fave_char(user_id, char_id):
    char_to_del = (
        db.session.query(Faves)
        .filter(Faves.user_id == user_id, Faves.fave_char == char_id)
        .first()
    )

    db.session.delete(char_to_del)
    db.session.commit()

    return "The force is with you", 200

# Fave Planets
@app.route('/favorites/user/<int:user_id>/planets/<int:planet_id>', methods=['POST'])
def create_fave_planet(user_id, planet_id):
    new_fave_planet = Faves(
        user_id = user_id,
        fave_planet = planet_id
        )

    db.session.add(new_fave_planet)
    db.session.commit()

    return "The force is with you", 200

@app.route('/favorites/user/<int:user_id>/planets/<int:planet_id>', methods=['DELETE'])
def del_fave_planet(user_id, planet_id):
    planet_to_del = (
        db.session.query(Faves)
        .filter(Faves.user_id == user_id, Faves.fave_planet == planet_id)
        .first()
    )

    db.session.delete(planet_to_del)
    db.session.commit()

    return "The force is with you", 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
