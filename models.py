from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    temperature = db.Column(db.Float)
    sbp = db.Column(db.Float)
    dbp = db.Column(db.Float)
    heart_rate = db.Column(db.Float)
    hrv = db.Column(db.Float)
    glucose = db.Column(db.Float)
    diagnosis = db.Column(db.String(100))
    insulin_dose = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
