"""Forms for the core app."""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, SelectField,\
    HiddenField, BooleanField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email

class SelectFieldNoValidate(SelectField):
    def pre_validate(self, form):
        pass

class MealTypeForm(FlaskForm):
    """Form for meal types."""

    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class DrinkForm(FlaskForm):
    """Form for editing drink items."""

    label = StringField('Label', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')

class SideForm(FlaskForm):
    """Form for editing side items."""

    label = StringField('Label', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')

class FoodForm(FlaskForm):
    """Form for editing foods."""

    label = StringField('Label', validators=[DataRequired()])
    description = StringField('Description')
    sides = SelectMultipleField('Choose Sides', \
        description='Use CTRL (Windows) or CMD (Mac) to select multiple sides.', coerce=int)
    submit = SubmitField('Save')

class DeleteForm(FlaskForm):
    """Form for deleting items."""

    item_type = HiddenField(validators=[DataRequired()])
    item_id = HiddenField(validators=[DataRequired()])

class MealDeleteForm(FlaskForm):
    """Form for deleting meals."""

    meal_id = HiddenField(validators=[DataRequired()])

class MealForm(FlaskForm):
    """Form for adding meals."""

    meal_type = SelectField('Meal Type', validators=[DataRequired()], coerce=int)
    restaurant = StringField('Restaurant')
    date = DateField('Date', validators=[DataRequired()])
    drinks = SelectMultipleField(
        'Choose Drinks',
        description='Use CTRL (Windows) or CMD (Mac) to select multiple drinks.',
        coerce=int,
        validators=[DataRequired()]
    )
    foods = SelectMultipleField(
        'Choose Foods',
        description='Use CTRL (Windows) or CMD (Mac) to select multiple drinks.',
        coerce=int,
        validators=[DataRequired()]
    )
    registration_open = BooleanField('Registration Open')
    submit = SubmitField('Save')

class ResponseForm(FlaskForm):
    """Form for signing up for a meal."""

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    meal_id = HiddenField(validators=[DataRequired()])
    food = SelectFieldNoValidate('Choose Meal', coerce=int, choices=[])
    food_other = StringField('Other Food', render_kw={'disabled':''})
    side = SelectFieldNoValidate('Choose a side', coerce=int, choices=[])
    side_other = StringField('Other Side', render_kw={'disabled':''})
    drink = SelectFieldNoValidate('Choose Drink', coerce=int, choices=[])
    drink_other = StringField('Other Drink', render_kw={'disabled':''})
    note = TextAreaField('Notes')
    submit = SubmitField('Submit')
