from datetime import datetime
from KYC_WalletApp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    account_address = db.Column(db.String(60), nullable=False)
    keystore = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<USER: {self.username}; {self.email}; {self.account_address}>"

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_name = db.Column(db.String(30), nullable=False)
    create_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    status = db.Column(db.String(20), nullable=False) # success or failure
    channel = db.Column(db.String(30), nullable=False) # api or console

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity = db.relationship('User',
                               backref=db.backref('activity_log', lazy=True))


    def __repr__(self):
        return f"<ACTIVITY: {self.request_name}; {self.create_datetime}; {self.status}>"
