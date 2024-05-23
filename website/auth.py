from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db # =  from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from .models import Role


auth_blueprint = Blueprint('auth_blueprint', __name__)


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

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, user_name=user_name, password=generate_password_hash(password1, method='pbkdf2:sha256'), role_id=role_id)
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



