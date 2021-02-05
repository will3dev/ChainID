from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, FloatField)
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from KYC_WalletApp.users.utils import *


class TransferForm(FlaskForm):
    to_address = StringField('Receiving Address', validators=[
        DataRequired(),
        Length(min=20, max=42)
    ])

    confirm_address = StringField('Confirm Address', validators=[
        DataRequired(),
        EqualTo('to_address')
    ])

    amount = FloatField('Ether to Send', validators=[
        DataRequired()
    ])

    password = PasswordField('Password', validators=[
        DataRequired()
    ])


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
    ])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=2, max=20)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already exists. Please a different one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email already exists. Please select a different one.')

    def validate_email_format(self, email):
        if not validate_emailTool(email):
            raise ValidationError('Not a valid email.')

    def validate_password(self, password):
        if not validate_password(password.data):
            raise ValidationError('Password does not meet criteria: 1 upper, 1 lower, 1 number, at least 8 characters.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
    ])

    password = PasswordField('Password', validators=[
        DataRequired()
    ])

    login = SubmitField('Login')

    def validate_email_format(self, email):
        if not validate_emailTool(email):
            raise ValidationError('Not a valid email.')