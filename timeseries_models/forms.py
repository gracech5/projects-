from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField

class arima(FlaskForm):
    submit = SubmitField('ARIMA Model')

class lstm(FlaskForm):
    submit = SubmitField('LSTM Model')