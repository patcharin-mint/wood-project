from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db # =  from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from .models import Role, Source, Wood
from werkzeug.utils import secure_filename
import os
import uuid


auth_blueprint = Blueprint('auth_blueprint', __name__)

UPLOAD_FOLDER = 'website/static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@auth_blueprint.route('/sign-up', methods=['GET', 'POST'])
def sign_up():

    roles = Role.query.all()

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        user_name = request.form.get('userName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role_id = request.form.get('role')

        if User.query.filter_by(email=email).first():
            flash('Email นี้มีผู้ใช้แล้ว', category='error')
        elif User.query.filter_by(user_name=user_name).first():
            flash('Username นี้มีผู้ใช้แล้ว', category='error')
        elif len(email) < 4 or len(email) > 50:
            flash('Email ต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร', category='error')
        elif len(user_name) < 4 or len(user_name) > 50:
            flash('Username ต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร', category='error')
        elif len(first_name) < 2  or len(first_name) > 50:
            flash('ชื่อจริงต้องมีขนาดตั้งแต่ 2 - 50 ตัวอักษร', category='error')
        elif len(last_name) < 2  or len(last_name) > 50:
            flash('นามสกุลต้องมีขนาดตั้งแต่ 2 - 50 ตัวอักษร', category='error')
        elif password1 != password2:
            flash('กรุณาใส่ Password ให้ตรงกัน', category='error')
        elif len(password1) < 7 or len(password1) > 50:
            flash('Password ต้องมีขนาดตั้งแต่ 7 - 50 ตัวอักษร', category='error')
        else:
            filename = None
            if 'profile_picture' in request.files:
                profile_picture = request.files['profile_picture']
            
                if profile_picture and allowed_file(profile_picture.filename):
                    filename = secure_filename(profile_picture.filename)
                    filename = f"{user_name}_profile.jpg"

                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    profile_picture.save(file_path)

            new_user = User(email=email, first_name=first_name, last_name=last_name, user_name=user_name, password=generate_password_hash(password1, method='pbkdf2:sha256'), role_id=role_id, profile_picture=filename)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')

            return redirect(url_for('views_blueprint.home'))

    return render_template("sign_up.html", user=current_user, roles=roles)



@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views_blueprint.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)



@auth_blueprint.route('/logout')
@login_required # ต้อง log in ก่อนถึงจะ log out ได้
def logout():
    logout_user()
    return redirect(url_for('auth_blueprint.login'))



@auth_blueprint.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    user = current_user

    can_update = False

    email = request.form.get('email')
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    user_name = request.form.get('userName')
    role_id = request.form.get('role')

    if User.query.filter(User.email == email, User.user_id != user.user_id).first():
        flash('Email นี้มีผู้ใช้แล้ว', category='error')
    elif User.query.filter(User.user_name == user_name, User.user_id != user.user_id).first():
        flash('Username นี้มีผู้ใช้แล้ว', category='error')
    elif len(email) < 4 or len(email) > 50:
        flash('Email ต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร', category='error')
    elif len(first_name) < 2  or len(first_name) > 50:
        flash('ชื่อจริงต้องมีขนาดตั้งแต่ 2 - 50 ตัวอักษร', category='error')
    elif len(last_name) < 2  or len(last_name) > 50:
        flash('นามสกุลต้องมีขนาดตั้งแต่ 2 - 50 ตัวอักษร', category='error')
    elif user_name != None:
        if len(user_name) < 4 or len(user_name) > 50:
            flash('Username ต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร', category='error')
        else:
            can_update = True
    else:
        can_update = True

    if can_update:
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if user_name != None:
            print(user_name)
            user.user_name = user_name

        if role_id != None:
            print(role_id)
            user.role_id = role_id


        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture and allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)
                filename = f"{user.user_name}_profile.jpg"

                file_path = os.path.join(UPLOAD_FOLDER, filename)

                if os.path.exists(file_path):
                    os.remove(file_path)

                profile_picture.save(file_path)
                user.profile_picture = filename
        
        db.session.commit()
        flash('Profile updated successfully!', category='success')

    return redirect(url_for('views_blueprint.profile'))




