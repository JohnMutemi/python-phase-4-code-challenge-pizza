from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize SQLAlchemy with custom metadata
db = SQLAlchemy(metadata=metadata)

# Define the Restaurant model
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    # Define columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Define relationships
    restaurant_pizzas = relationship("RestaurantPizza", back_populates="restaurant", cascade="all, delete")
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    # Define serialization rules to avoid recursion
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def _repr_(self):
        return f"<Restaurant {self.name}>"

# Define the Pizza model
class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    # Define columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Define relationships
    restaurant_pizzas = relationship("RestaurantPizza", back_populates="pizza", cascade="all, delete")
    restaurants = association_proxy("restaurant_pizzas", "restaurant")
    
    # Define serialization rules avoid recursion
    serialize_rules = ('-restaurant_pizzas.pizza',)

    def _repr_(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

# Define the RestaurantPizza model
class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    # Define columns
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'), nullable=False)

    # Define relationships
    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")

    # Define serialization rules to exclude circular references
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    # Define validation for the price field
    @validates('price')
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30")
        return value

    def _repr_(self):
        return f"<RestaurantPizza ${self.price}>"
