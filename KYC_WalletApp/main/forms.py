from flask_wtf import FlaskForm
from wtforms import (StringField)
from wtforms.validators import DataRequired, Length, ValidationError
from KYC_WalletApp.w3.Wallet_Factory import Wallet_Factory as wf

class WalletSearchForm(FlaskForm):
    search = StringField("Search", validators=[
        DataRequired(),
    ])

