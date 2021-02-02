
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2313@localhost/CharitySystem'

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'userDetails'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    occupation = db.Column(db.String, nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String,nullable=False)
    image = db.Column(db.String(120), default='default.jpg')
    password = db.Column(db.String, nullable=False)


class Charity(db.Model):
    __tablename__ = 'charityDetails'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(120),default='image.jpg')
    pub_time = db.Column(db.Date, nullable=False,default=datetime.utcnow)


class Donation(db.Model):
    __tablename__ = 'donationDetails'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.String, nullable=False)
    reciever = db.Column(db.String, nullable=False)
    donor_email = db.Column(db.String, nullable=False)
    transaction_id = db.Column(db.String, nullable=False)
    transaction_amount = db.Column(db.Integer, nullable=False)
    transaction_time = db.Column(db.Time, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)


class Suggestion(db.Model):
    __tablename__ = 'userSuggestion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False)
    image = db.Column(db.String(120),default='image.jpg')
    subject = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)


