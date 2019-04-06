"""Core application routes."""

import re
import csv
import io
from flask import render_template, flash, redirect, url_for, jsonify,\
    make_response
from flask_login import login_required
from app import db
from app.main import bp
from app.main.models import Meal, Drink, Side, Food, MealType, Response
from app.main.forms import DrinkForm, SideForm, FoodForm, MealTypeForm,\
    DeleteForm, MealForm, MealDeleteForm, ResponseForm
import app
import app.main.forms

@bp.route('/')
@bp.route('/index')
def index():
    meals = Meal.query.filter_by(registration_open=True).order_by(Meal.date).all()

    return render_template('index.html', title='Meal Sign-up', meals=meals)

@bp.route('/respond/<meal_id>', methods=['GET', 'POST'])
def respond(meal_id):
    meal = Meal.query.get(meal_id)
    form = ResponseForm()

    foods = meal.foods.all()

    form.food.choices = [
        (food.id, f'{food.label} {f"({food.description})" if food.description else ""}') \
            for food in foods
    ]
    form.food.choices.append(("0", "Other"))

    form.drink.choices = [(drink.id, drink.label)\
        for drink in meal.drinks.order_by(Drink.label).all()]
    form.drink.choices.append(("0", "Other"))

    form.side.choices = [(side.id, side.label)\
        for side in foods[0].sides.order_by(Side.label).all()]
    # Can only get "other" side if we have choice of at least one side
    if form.side.choices:
        form.side.choices.append(("0", "Other"))

    if form.validate_on_submit():
        response = Response(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            food_other=form.food_other.data,
            drink_other=form.drink_other.data,
            side_other=form.side_other.data,
            note=form.note.data
        )

        if form.food.data:
            response.food_id = form.food.data
        if form.side.data:
            response.side_id = form.side.data
        if form.drink.data:
            response.drink_id = form.drink.data

        response.meal = Meal.query.get(form.meal_id.data)

        db.session.add(response)
        db.session.commit()

        flash('Your order was submitted successfully!', 'success')
        return redirect(url_for('main.index'))

    else:
        form.meal_id.data = meal_id

    return render_template('respond.html', meal=meal, form=form)

@bp.route('/responses/<meal_id>', methods=['GET'])
def responses(meal_id):

    meal = Meal.query.get(meal_id)

    if meal:

        csv_io = io.StringIO()
        writer = csv.writer(csv_io)

        writer.writerow(
            [
                'First Name',
                'Last Name',
                'Email',
                'Food',
                'Side',
                'Drink',
                'Note',
                'Timestamp'
            ]
        )

        for entry in meal.responses:
            cur = []

            cur.append(entry.first_name)
            cur.append(entry.last_name)
            cur.append(entry.email)

            if entry.food:
                cur.append(entry.food.label)
            else:
                cur.append(entry.food_other)

            if entry.side:
                cur.append(entry.side.label)
            else:
                cur.append(entry.side_other)

            if entry.drink:
                cur.append(entry.drink.label)
            else:
                cur.append(entry.drink_other)

            cur.append(entry.note)
            cur.append(entry.timestamp)

            writer.writerow(cur)

        response = make_response(csv_io.getvalue())
        response.headers['Content-type'] = 'text/csv'
        response.headers['Content-Disposition'] =\
            f'attachment; filename={meal.date} {meal.meal_type.name}.csv'

        return response

    flash('Could not find that meal!', 'danger')
    return redirect(url_for('main.meal_list'))

@bp.route('/sides/<food_id>')
def sides(food_id):

    food = Food.query.get(food_id)

    side_list = [
        {
            'id': side.id,
            'label': side.label,
            'description': side.description
        } for side in food.sides.order_by(Side.label).all()
    ]

    # Can only get "other" side if we have at least one side
    if side_list:
        side_list.append({
            'id': 0,
            'label': 'Other',
            'description': 'Choose another side.'
        })

    return jsonify({'sides': side_list})

# Meal Management 
# region
@bp.route('/meal_list')
@login_required
def meal_list():
    form = MealDeleteForm()
    meals = Meal.query.order_by(Meal.date).all()

    return render_template('meal_list.html', meals=meals, title='Meals List', form=form)

@bp.route('/meal_edit/<meal_id>', methods=['GET', 'POST'])
@bp.route('/meal_edit', methods=['GET', 'POST'])
@login_required
def meal_edit(meal_id=None):

    title_message = 'Create'

    form = MealForm()
    form.meal_type.choices = [(meal_type.id, meal_type.name) for meal_type in \
        MealType.query.order_by(MealType.name).all()]
    form.drinks.choices = [(drink.id, drink.label) for drink in \
        Drink.query.order_by(Drink.label).all()]
    form.foods.choices = [(food.id, food.label) for food in \
        Food.query.order_by(Food.label).all()]

    # If meal_id not specified, this is a create
    if not meal_id:
        if form.validate_on_submit():
            meal = Meal(
                restaurant=form.restaurant.data,
                date=form.date.data,
                registration_open=form.registration_open.data
            )

            meal_type = MealType.query.get(form.meal_type.data)
            meal.meal_type = meal_type

            for drink_id in form.drinks.data: 
                meal.drinks.append(Drink.query.get(drink_id))
            for food_id in form.foods.data: 
                meal.foods.append(Food.query.get(food_id))

            db.session.add(meal)
            db.session.commit()

            flash(f'{meal_type.name} for {meal.date} was successfully created!', 'success')
            return redirect(url_for('main.meal_list'))

    # This is an edit. If it's not a submit, we'll populate the form.
    else:
        title_message = 'Edit'

        meal = Meal.query.get(meal_id)

        if form.validate_on_submit():
            meal.meal_type = MealType.query.get(form.meal_type.data)
            meal.restaurant = form.restaurant.data
            meal.date = form.date.data

            for drink in meal.drinks.all():
                meal.drinks.remove(drink)

            for drink_id in form.drinks.data:
                meal.drinks.append(Drink.query.get(drink_id))

            for food in meal.foods.all():
                meal.foods.remove(food)

            for food_id in form.foods.data:
                meal.foods.append(Food.query.get(food_id))

            meal.registration_open = form.registration_open.data

            db.session.commit()

            flash(f'Successfully updated {meal.meal_type.name} on {meal.date}', 'success')
            return redirect(url_for('main.meal_list'))

        else:
            if meal:
                form.meal_type.data = meal.meal_type.id
                form.restaurant.data = meal.restaurant
                form.date.data = meal.date
                form.drinks.data = [drink.id for drink in meal.drinks]
                form.foods.data = [food.id for food in meal.foods]
                form.registration_open.data = meal.registration_open

            else:
                flash('You attempted to edit a meal that does not exist.', 'danger')
                return redirect(url_for('main.meal_list'))

    return render_template('generic_form.html', form=form, title=f'{title_message} Meal')

@bp.route('/meal_delete', methods=['POST'])
@login_required
def meal_delete():

    form = MealDeleteForm()

    if form.validate_on_submit():

        meal = Meal.query.get(form.meal_id.data)

        if meal:
            meal_type_name = meal.meal_type.name
            db.session.delete(meal)
            db.session.commit()
            flash(f'{meal_type_name} on {meal.date} deleted!', 'success')
        else:
            flash('Could not find meal to delete.', 'danger')

        return redirect(url_for('main.meal_list'))
    
    return redirect(url_for('main.index'))

# endregion

# Item management (sides, drinks, foods, etc.)
# region
@bp.route('/item_list/<item_type>')
@login_required
def item_list(item_type):
    """List items."""

    type_lower = item_type.lower()
    type_cased = to_type_case(item_type)

    try:
        model = getattr(app.main.models, type_cased)
    except AttributeError:
        flash('Unknown datatype "{item_type}".', 'danger')
        return redirect(url_for('main.index'))

    data = model.query.order_by(
        model.name if model == MealType else model.label
    ).all()

    form = DeleteForm()

    return render_template('item_list.html', data=data, \
        title=f'{type_cased} List', item_type=type_cased, type_lower=type_lower, form=form)

@bp.route('/item_edit/<item_type>/<item_id>', methods=['GET', 'POST'])
@bp.route('/item_edit/<item_type>', methods=['GET', 'POST'])
@login_required
def item_edit(item_type, item_id=None):
    """Edit and create new meal items."""

    type_cased = to_type_case(item_type)

    try:
        form = getattr(app.main.forms, f'{type_cased}Form')()
        model = getattr(app.main.models, type_cased)
    except AttributeError:
        flash('Unknown datatype "{item_type}".', 'danger')
        return redirect(url_for('main.index'))

    title_message = 'Create'

    # Hangle model-specific setup here
    if model == Food:
        form.sides.choices = [(side.id, side.label) for side in Side.query.all()]

    # If item_id not specified, we're creating
    if not item_id:

        if form.validate_on_submit():
            if model == MealType:
                datum = model(
                    name=form.name.data
                )
            else:
                datum = model(
                    label=form.label.data,
                    description=form.description.data
                )

            # Handle model-specific choice assignment here
            if model == Food:
                for side_id in form.sides.data:
                    datum.sides.append(Side.query.get(side_id))

            db.session.add(datum)
            db.session.commit()

            flash(f'{datum.name if model == MealType else datum.label} was created!', 'success')
            return redirect(url_for('main.item_list', item_type=item_type.lower()))

    # If item_id is specified, we're editing
    else:
        title_message = 'Edit'

        # Validate the id we've received and apply to edit form
        datum = model.query.get(item_id)
        if not form.validate_on_submit():
            if datum:
                if model == MealType:
                    form.name.data = datum.name
                else:
                    form.label.data = datum.label
                    form.description.data = datum.description

                # Handle model-specific edit form value assignment here
                if model == Food:
                    form.sides.data = [side.id for side in datum.sides.all()]
            else:
                flash(f'You attempted to edit a {item_type} that does not exist.', 'danger')
                return redirect(url_for('main.item_list', item_type=item_type))

        # Save if we've received valid data
        if form.validate_on_submit():
            if model == MealType:
                datum.name = form.name.data
            else:
                datum.label = form.label.data
                datum.description = form.description.data

            if model == Food:
                for side in datum.sides.all():
                    datum.sides.remove(side)
                for side_id in form.sides.data:
                    datum.sides.append(Side.query.get(side_id))

            db.session.commit()

            flash(f'{datum.name if model == MealType else datum.label} updated!', 'success')
            return redirect(url_for('main.item_list', item_type=item_type))

    return render_template('generic_form.html', form=form, title=f'{title_message} {type_cased}')

@bp.route('/item_delete', methods=['POST'])
@login_required
def item_delete():
    """Delete specified item."""

    form = DeleteForm()

    if form.validate_on_submit():
        item_type = form.item_type.data
        item_id = form.item_id.data
        type_cased = to_type_case(item_type)

        try:
            model = getattr(app.main.models, type_cased)
        except AttributeError:
            flash('Unknown datatype "{item_type}".', 'danger')
            return redirect(url_for('main.index'))

        datum = model.query.get(item_id)

        if datum:
            db.session.delete(datum)
            db.session.commit()
            flash(f'{datum.name if model == MealType else datum.label} deleted!', 'success')
        else:
            flash('Could not find the specified item.', 'danger')

        return redirect(url_for('main.item_list', item_type=item_type.lower()))

    return redirect(url_for('main.index'))
# endregion

def to_type_case(item_type):
    """Convert the supplied item_type to the correct case."""

    # Handle first letter
    type_string = f'{item_type[0].upper()}{item_type[1:].lower()}'.strip()

    # Handle underscores
    type_string = re.sub(r'_([a-z])', lambda match: f'{match.group(1).upper()}', type_string)

    return type_string