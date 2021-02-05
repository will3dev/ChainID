import re
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, IntegerField,
                     PasswordField, SelectMultipleField)
from wtforms.validators import DataRequired, Length, ValidationError


class GetWalletDataForm_2(FlaskForm):
    request = SelectMultipleField(u"Wallet Address")

    password = PasswordField("Password", validators=[
        DataRequired()
    ])

class GetWalletDataForm(FlaskForm):
    wallet = StringField("Wallet Address", validators=[
        DataRequired()
    ])

    requester = StringField("Originator Address", validators=[
         DataRequired(),
     ])

    password = PasswordField("Password", validators=[
        DataRequired(),
    ])

    submit = SubmitField("Approve")


class ApproveWalletForm(FlaskForm):
    requester = StringField("Requester Wallet", validators=[
        DataRequired()
    ])

    password = PasswordField("Password", validators=[
        DataRequired(),
    ])

    submit = SubmitField("Approve")


class CreateWalletForm(FlaskForm):
    name = StringField("Full Name", validators=[
        DataRequired(),
    ])

    street = StringField("Street Address", validators=[
        DataRequired(),
    ])

    city = StringField("City", validators=[
        DataRequired(),
    ])

    state = StringField("State", validators=[
        DataRequired(),
    ])

    tin = StringField("Tax ID", validators=[
        DataRequired(),
    ])

    phone = StringField("Phone", validators=[
        DataRequired(),
    ])

    password = PasswordField("Password", validators=[
        DataRequired()
    ])

    # submit = SubmitField("Create Wallet")

    def validate_phone(self, phone):
        p = re.compile(r"""(\d{3}|\(\d{3}\))
                           (-?)
                           (\d{3})
                           (-?)
                           (\d{4})""", re.X)
        if not p.match(phone.data):
            raise ValidationError("Not a valid phone number format.")

    def validate_tin(self, tin):
        t = re.compile(r"""((\d{3})
                           (-?)
                           (\d{2})
                           (-?)
                           (\d{4})
                           |
                           (\d{9}))""", re.X)
        if not t.match(tin.data):
            raise ValidationError("Not a valid Tax ID format")


class RequestDataForm(FlaskForm):
    requester = StringField('Requester Name', validators=[
        DataRequired(),
        Length(min=2, max=20)
    ])

    request_reason = StringField('Reason for Request', validators=[
        DataRequired(),
        Length(min=2, max=60)
    ])

    password = PasswordField('Password', validators=[
        DataRequired()
    ])
