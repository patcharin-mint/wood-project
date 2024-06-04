from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Role(db.Model):
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)


    def get_id(self):
        return str(self.role_id)
    
    def get_name(self):
        return str(self.role_name)
    
    def get_user_count(self):
        return User.query.filter_by(role_id=self.role_id).count()
    


class Wood(db.Model):
    wood_id = db.Column(db.Integer, primary_key=True)
    wood_name = db.Column(db.String(50), unique=True, nullable=False)
    wood_nickname = db.Column(db.String(50), unique=True, nullable=False)

    def get_id(self):
        return str(self.wood_id)
    
    def get_name(self):
        return str(self.wood_name)
    
    def get_related_users(self):
        return User.query.filter_by(wood_id=self.wood_id).all()



class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    role_id = db.Column(db.String(50), db.ForeignKey('role.role_id'), nullable=False)
    profile_picture = db.Column(db.String(100), unique=True)

    role = db.relationship('Role', backref='users') 
    posts = db.relationship('Post')

    def get_id(self):
        return str(self.user_id)



class PredictRecord(db.Model):
    record_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user_role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('source.source_id'), nullable=False)
    wood_id = db.Column(db.Integer, db.ForeignKey('wood.wood_id'), nullable=False) 
    file_name = db.Column(db.String(100), unique=True, nullable=False)
    prob1 = db.Column(db.String(50), nullable=False)
    prob2 = db.Column(db.String(50), nullable=False)
    prob3 = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', foreign_keys=[user_id])
    source = db.relationship('Source', foreign_keys=[source_id])
    wood = db.relationship('Wood', foreign_keys=[wood_id])
    role = db.relationship('Role', foreign_keys=[user_role_id])

    def get_id(self):
        return str(self.record_id)


class Source(db.Model):
    source_id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(50), unique=True, nullable=False)

    predict_records = db.relationship('PredictRecord')

    def get_id(self):
        return str(self.source_id)
    
    def get_name(self):
        return str(self.source_name)


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_post_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user_role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), nullable=False)
    datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)

    files = db.relationship('File')
    role = db.relationship('Role', foreign_keys=[user_role_id])
    user_post = db.relationship('User', foreign_keys=[user_post_id])
    category_post = db.relationship('Category', foreign_keys=[category_id])


class File(db.Model):
    file_id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), unique=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)


class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(20), unique=True, nullable=False)


