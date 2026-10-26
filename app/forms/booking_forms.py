from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class AvailabilitySearchForm(FlaskForm):
    check_in = DateField('Check-in Date', validators=[DataRequired()])
    check_out = DateField('Check-out Date', validators=[DataRequired()])
    guests = IntegerField('Number of Guests', validators=[DataRequired(), NumberRange(min=1, max=20)], default=2)
    submit = SubmitField('Check Availability')

class BookingForm(FlaskForm):
    accommodation_unit_id = SelectField('Selected Accommodation', coerce=int, validators=[DataRequired()])
    check_in = DateField('Check-in Date', validators=[DataRequired()])
    check_out = DateField('Check-out Date', validators=[DataRequired()])
    guests = IntegerField('Number of Guests', validators=[DataRequired(), NumberRange(min=1, max=20)])
    special_requests = TextAreaField('Special Requests / Notes (Optional)')
    submit = SubmitField('Submit Reservation Request')
