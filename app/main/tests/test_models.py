"""Test core app models."""

import unittest
from datetime import datetime, timedelta
from config import Config
from app import create_app
from app import db
from app.main.models import MealType, Meal, Drink, Food, Side, Response
from app.tests.test_utils import ModelTestMixin

class TestMealsAndTypes(ModelTestMixin, unittest.TestCase):
    """Tests for the meal type model."""

    def test_mealtype_create(self):
        """Test creating a meal type."""

        meal_types = [
            MealType(name='Breakfast'),
            MealType(name='Lunch'),
            MealType(name='Dinner')
        ]

        db.session.add_all(meal_types)
        db.session.commit()

        self.assertEqual(3, len(MealType.query.all()))

        breakfast = MealType.query.filter_by(name='Breakfast').first()

        self.assertEqual('Breakfast', breakfast.name)

    def test_meal_create(self):
        """Test creating a meal, ensure many-to-one relationship to MealType works."""

        breakfast = MealType(name="Breakfast")
        db.session.add(breakfast)

        db.session.add(
            Meal(
                meal_type=breakfast,
                restaurant='Restaurant Awesome',
                date=datetime.utcnow().date() + timedelta(days=2),
                registration_open=datetime.utcnow() - timedelta(days=1),
                registration_close=datetime.utcnow() + timedelta(days=1)
            )
        )
        db.session.commit()


        self.assertEqual(1, len(Meal.query.all()))

        meal = Meal.query.first()
        self.assertEqual("Breakfast", meal.meal_type.name)

        meal2 = breakfast.meals.first()
        self.assertEqual(meal, meal2)
        self.assertEqual('Restaurant Awesome', meal2.restaurant)

    def test_get_open_meals(self):
        """Ensure the function for getting open meals works as expected.

        We expect open meals to be sorted asc. by closing date.
        """

        breakfast = MealType(name="Breakfast")
        lunch = MealType(name="Lunch")

        early = Meal(
            meal_type=breakfast,
            date=datetime.utcnow().date() + timedelta(days=5),
            registration_open=datetime.utcnow() + timedelta(days=3),
            registration_close=datetime.utcnow()+ timedelta(days=4)
        )

        open1 = Meal(
            meal_type=breakfast,
            date=datetime.utcnow().date() + timedelta(days=1),
            registration_open=datetime.utcnow() - timedelta(days=1),
            registration_close=datetime.utcnow() + timedelta(hours=6)
        )

        open2 = Meal(
            meal_type=lunch,
            date=datetime.utcnow().date() + timedelta(days=1),
            registration_open=datetime.utcnow() - timedelta(hours=6),
            registration_close=datetime.utcnow() + timedelta(hours=12)
        )

        late = Meal(
            meal_type=lunch,
            date=datetime.utcnow().date() - timedelta(days=1),
            registration_open=datetime.utcnow() - timedelta(days=3),
            registration_close=datetime.utcnow() - timedelta(days=1)
        )

        db.session.add_all([
            early,
            open1,
            open2,
            late
        ])

        open_meals = Meal.get_open_meals()

        self.assertListEqual([open1, open2], open_meals)

class TestChoices(ModelTestMixin, unittest.TestCase):
    """Tests to verify that item choice models exist."""

    def test_drink(self):
        """Verify creation of drink items."""

        drink1 = Drink(label='Orange Juice', description='Fresh squeezed goodness.')
        drink2 = Drink(label='Coffee', description='The juice of life.')

        db.session.add_all([drink1, drink2])
        db.session.commit()

        self.assertListEqual([drink2, drink1], Drink.query.order_by(Drink.label).all())
        self.assertIsNotNone(drink1.label)
        self.assertIsNotNone(drink1.description)

    def test_food(self):
        """Verify creation of food items."""

        food1 = Food(label='Cheese Pizza', description='Pure awesomeness.')
        food2 = Food(label='Hamburger', description='Beef on a bun.')

        db.session.add_all([food1, food2])
        db.session.commit()

        self.assertListEqual([food1, food2], Food.query.order_by(Food.label).all())
        self.assertIsNotNone(food1.label)
        self.assertIsNotNone(food1.description)

    def test_side(self):
        """Verify creation of side items."""

        side1 = Side(label='French Fries', description='Salted starch.')
        side2 = Side(label='Mashed Potatoes', description='Pulverized starch.')

        db.session.add_all([side1, side2])
        db.session.commit()

        self.assertListEqual([side1, side2], Side.query.order_by(Side.label).all())
        self.assertIsNotNone(side1.label)
        self.assertIsNotNone(side1.description)

class TestManyManyRelationships(ModelTestMixin, unittest.TestCase):
    """Test many-to-many relationships between meals, drinks, food, and sides."""

    def test_meal_drink(self):
        """Verify many-to-many between meals and drinks."""

        breakfast = MealType(name='Breakfast')

        orange_juice = Drink(label='Orange Juice', description='Fresh squeezed.')
        coffee = Drink(label='Coffee', description='High octane.')
        tea = Drink(label='Tea', description='Only the finest.')

        meal = Meal(
            meal_type=breakfast,
            date=datetime.utcnow().date(),
            registration_open=datetime.utcnow() - timedelta(days=1),
            registration_close=datetime.utcnow() + timedelta(days=1)
        )

        for drink in [orange_juice, coffee]:
            meal.drinks.append(drink)

        db.session.add_all([breakfast, orange_juice, coffee, tea, meal])
        db.session.commit()

        meal_drinks = meal.drinks.order_by(Drink.label).all()

        self.assertListEqual([coffee, orange_juice], meal_drinks)
        self.assertEqual(meal, orange_juice.meals.first())

    def test_meal_food(self):
        """Verify many-to-many relationship between meals and foods."""

        dinner = MealType(name="Dinner")

        pizza = Food(label='Cheese Pizza', description='Pure awesomeness.')
        hamburger = Food(label='Hamburger', description='Beef on a bun.')
        chicken = Food(label='Chicken', description='Poultry.')

        meal = Meal(
            meal_type=dinner,
            date=datetime.utcnow().date(),
            registration_open=datetime.utcnow() - timedelta(days=1),
            registration_close=datetime.utcnow() + timedelta(days=1)
        )

        for food in [hamburger, chicken]:
            meal.foods.append(food)

        db.session.add_all([dinner, pizza, hamburger, chicken, meal])
        db.session.commit()

        meal_foods = meal.foods.order_by(Food.label).all()

        self.assertListEqual([chicken, hamburger], meal_foods)
        self.assertEqual(meal, chicken.meals.first())

    def test_food_sides(self):
        """Verify many to many relationship between foods and sides."""

        chicken = Food(label="Chicken", description="Poultry")
        hamburger = Food(label="Cheeseburger", description="Beef and cheese on a bun.")

        fries = Side(label="Fries")
        rice = Side(label="Rice")
        mashed = Side(label="Mashed Potatoes")

        for side in [rice, mashed]:
            chicken.sides.append(side)

        for side in [fries, rice]:
            hamburger.sides.append(side)

        db.session.add_all([chicken, hamburger, fries, rice, mashed])
        db.session.commit()

        chicken_sides = chicken.sides.order_by(Side.label).all()
        burger_sides = hamburger.sides.order_by(Side.label).all()

        self.assertListEqual([mashed, rice], chicken_sides)
        self.assertListEqual([fries, rice], burger_sides)

        self.assertEqual(hamburger, fries.foods.first())

        rice_foods = rice.foods.order_by(Food.label).all()
        self.assertListEqual([hamburger, chicken], rice_foods)

class TestResponse(ModelTestMixin, unittest.TestCase):
    """Verify the response object."""

    def test_response(self):
        """Test response objects."""

        # Mock some test meal data

        lunch = MealType(name='Lunch')

        tea = Drink(label='Tea')
        coffee = Drink(label='Coffee')

        hamburger = Food(label='Hamburger')
        chicken = Food(label='Chicken')

        fries = Side(label='Fries')
        mashed = Side(label='Mashed Potatoes')
        rice = Side(label='Rice')

        for side in [fries, rice]:
            hamburger.sides.append(side)

        for side in [mashed, rice]:
            chicken.sides.append(side)

        lunch_meal = Meal(
            meal_type=lunch,
            date=datetime.utcnow().date() + timedelta(days=1),
            registration_open=datetime.utcnow() - timedelta(days=1),
            registration_close=datetime.utcnow() + timedelta(days=1)
        )

        for drink in [tea, coffee]:
            lunch_meal.drinks.append(drink)

        for food in [hamburger, chicken]:
            lunch_meal.foods.append(food)

        db.session.add_all([
            lunch,
            tea,
            coffee,
            hamburger,
            chicken,
            fries,
            rice,
            mashed,
            lunch_meal
        ])
        db.session.commit()

        # Create three responses

        response1 = Response(
            first_name='Paul',
            last_name='Revere',
            email='paul@rider.com',
            note='Liberty!'
        )

        response1.meal = lunch_meal
        response1.drink = tea
        response1.food = hamburger
        response1.side = fries


        response2 = Response(
            first_name='John',
            last_name='Hancock',
            email='john@signers.com',
            note='I like lots of cheese!'
        )

        response2.meal = lunch_meal
        response2.drink = coffee
        response2.food = chicken
        response2.side = fries

        response3 = Response(
            first_name='Thomas',
            last_name='Jefferson',
            email='tom@framers.com',
            note='I don\'t like anything on this menu.'
        )

        response3.meal = lunch_meal
        response3.food_other = 'Filet Mignon'
        response3.drink_other = 'Wine'
        response3.side_other = 'Mixed Vegetables'

        db.session.add_all([response1, response2, response3])
        db.session.commit()

        # Verify expected behavior (incl. meal cascading delete)

        self.assertEqual(3, len(Response.query.all()))

        db_response_1 = Response.query.filter_by(email='paul@rider.com').first()

        self.assertLess(1, (datetime.utcnow() - db_response_1.timestamp).microseconds)

        self.assertEqual(lunch_meal, db_response_1.meal)
        self.assertEqual(hamburger, db_response_1.food)

        db_response_3 = Response.query.filter_by(email='tom@framers.com').first()

        self.assertEqual('Filet Mignon', db_response_3.food_other)
        self.assertEqual('Wine', db_response_3.drink_other)

        db_response_2 = Response.query.filter_by(email="john@signers.com").first()
        db.session.delete(db_response_2)
        db.session.commit()

        self.assertEqual(2, len(Response.query.all()))
        self.assertEqual(1, len(Meal.query.all()))

        db.session.delete(lunch_meal)
        db.session.commit()

        self.assertEqual(0, len(Response.query.all()))
