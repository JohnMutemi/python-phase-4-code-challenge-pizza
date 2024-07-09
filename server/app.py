#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize the Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


api = Api(app)
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Define a resource for handling GET requests to retrieve all restaurants
class Restaurants(Resource):
    def get(self):
        # Query all restaurants and convert them to dictionaries excluding the 'restaurant_pizzas' relationship
        restaurants = [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in Restaurant.query.all()]
        response = make_response(restaurants, 200)
        return response

# Define a resource for handling GET and DELETE requests for a specific restaurant by ID
class RestaurantByID(Resource):
    def get(self, id):
    
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant:
            response = make_response(restaurant.to_dict(), 200)
            return response
        else:
            return {'error': 'Restaurant not found'}, 404

    def delete(self, id):
        # Query a restaurant by ID
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
        else:
            return {'error': 'Restaurant not found'}, 404

# Define a resource for handling GET requests to retrieve all pizzas
class Pizzas(Resource):
    def get(self):
        # Query all pizzas and convert them to dictionaries excluding the 'restaurant_pizzas' relationship
        pizzas = [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in Pizza.query.all()]
        response = make_response(jsonify(pizzas), 200)
        return response

# Define a resource for handling POST requests to create a new restaurant-pizza relationship
class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        
        # Validate the price
        if data.get('price') is None or not (1 <= data['price'] <= 30):
            return {'errors': ["validation errors"]}, 400
        
        pizza = Pizza.query.get(data['pizza_id'])
        restaurant = Restaurant.query.get(data['restaurant_id'])
        
        if not pizza or not restaurant:
            return {'errors': ["validation errors"]}, 400
        
        # Create a new RestaurantPizza entry
        new_restaurant_pizza = RestaurantPizza(
            price = data['price'],
            pizza_id = data['pizza_id'],
            restaurant_id = data['restaurant_id']
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        new_restaurant_pizza_dict = new_restaurant_pizza.to_dict()
        response = make_response(new_restaurant_pizza_dict, 201)
        return response

# Add resource endpoints to the API
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

# Run the app if this script is executed directly
if __name__ == "__main__":
    app.run(port=5555, debug=True)
