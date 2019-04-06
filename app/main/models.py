"""Database models for the primary app functionality."""

from datetime import datetime
from app import db

# region
# Association table for meals and drinks
meal_drink = db.Table( #pylint: disable=invalid-name
    'meal_drink',
    db.Column('meal_id', db.Integer, db.ForeignKey('meal.id'), primary_key=True),
    db.Column('drink_id', db.Integer, db.ForeignKey('drink.id'), primary_key=True)
)

# Association table for meals and foods
meal_food = db.Table( #pylint: disable=invalid-name
    'meal_food',
    db.Column('meal_id', db.Integer, db.ForeignKey('meal.id'), primary_key=True),
    db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True)
)

# Association table for foods and sides
food_side = db.Table( #pylint: disable=invalid-name
    'food_side',
    db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True),
    db.Column('side_id', db.Integer, db.ForeignKey('side.id'), primary_key=True)
)
# endregion

class MealType(db.Model):
    """The type of meal (breakfast, lunch, dinner, brunch, etc.)"""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), index=True, nullable=False)
    meals = db.relationship('Meal', backref='meal_type', lazy='dynamic')

    def __repr__(self):
        return f"<MealType: {self.id}, {self.name}>"

class Meal(db.Model):
    """Represents an individual meal that will take place."""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    meal_type_id = db.Column(db.Integer, db.ForeignKey('meal_type.id'))
    restaurant = db.Column(db.String(128))
    date = db.Column(db.Date, nullable=False)
    registration_open = db.Column(db.Boolean, nullable=False, default=False)
    drinks = db.relationship(
        'Drink',
        secondary=meal_drink,
        backref=db.backref('meals', lazy='dynamic'),
        lazy='dynamic'
    )
    foods = db.relationship(
        'Food',
        secondary=meal_food,
        backref=db.backref('meals', lazy='dynamic'),
        lazy='dynamic'
    )

    @staticmethod
    def get_open_meals():
        """Get currently available meals for registration."""

        return Meal.query.filter(
            Meal.registration_open < datetime.utcnow(),
            Meal.registration_close > datetime.utcnow()
        ).order_by(Meal.registration_close).all()

class Drink(db.Model):
    """Represents a possible drink choice."""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    label = db.Column(db.String(140), nullable=False)
    description = db.Column(db.String(250))

class Food(db.Model):
    """Represents a possible food choice."""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    label = db.Column(db.String(140), nullable=False)
    description = db.Column(db.String(250))
    sides = db.relationship(
        'Side',
        secondary=food_side,
        backref=db.backref('foods', lazy='dynamic'),
        lazy='dynamic'
    )

class Side(db.Model):
    """Represents a possible side choice."""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    label = db.Column(db.String(140), nullable=False)
    description = db.Column(db.String(250))

class Response(db.Model):
    """Represents a meal choice response."""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64))
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    meal = db.relationship(
        'Meal',
        backref=db.backref('responses', lazy='dynamic', cascade="all, delete-orphan"),
    )
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'))
    food = db.relationship(
        'Food',
        backref=db.backref('responses', lazy='dynamic')
    )
    drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'))
    drink = db.relationship(
        'Drink',
        backref=db.backref('responses', lazy='dynamic')
    )
    side_id = db.Column(db.Integer, db.ForeignKey('side.id'))
    side = db.relationship(
        'Side',
        backref=db.backref('responses', lazy='dynamic')
    )
    food_other = db.Column(db.String(140))
    drink_other = db.Column(db.String(140))
    side_other = db.Column(db.String(140))
    note = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
