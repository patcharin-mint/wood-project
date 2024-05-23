from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Role(db.Model, UserMixin):
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

    def get_id(self):
        return str(self.role_id)


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    role_id = db.Column(db.String(50), db.ForeignKey('role.role_id'), nullable=False)

    def get_id(self):
        return str(self.user_id)


class PredictRecord(db.Model):
    record_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('source.source_id'), nullable=False)
    file_name = db.Column(db.String(100), unique=True, nullable=False)
    prob1 = db.Column(db.String(50), nullable=False)
    prob2 = db.Column(db.String(50), nullable=False)
    prob3 = db.Column(db.String(50), nullable=False)

    def get_id(self):
        return str(self.record_id)


class Source(db.Model):
    source_id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(50), unique=True, nullable=False)

    def get_id(self):
        return str(self.source_id)
