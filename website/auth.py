from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, create_app # =  from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from .models import Role, Source, Wood, Category
from werkzeug.utils import secure_filename
import os
import locale
import requests


auth_blueprint = Blueprint('auth_blueprint', __name__)

PROFILE_FOLDER = 'website/static/profiles'
STATIC_IMG_FOLDER = 'website/static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

G_LEN_EMAIL = 4
G_LEN_FNAME = 2
G_LEN_LNAME = 2
G_LEN_UNAME = 4
G_LEN_PWORD = 7
NG_LEN_EMAIL = 50
NG_LEN_FNAME = 50
NG_LEN_LNAME = 50
NG_LEN_UNAME = 50
NG_LEN_PWORD = 50

# ตั้งค่า locale เป็น 'th_TH.UTF-8' เพื่อให้ Python รู้จักการเรียงลำดับภาษาไทย
locale.setlocale(locale.LC_COLLATE, 'th_TH.UTF-8')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# route

@auth_blueprint.route('/sign-up', methods=['GET', 'POST'])
def sign_up():

    # กำหนด key ในการเรียงลำดับตามตัวอักษรภาษาไทย
    sorted_roles = sorted(Role.query.all(), key=lambda x: locale.strxfrm(x.role_name))

    if request.method == 'POST':
        
        print(request.form)

        secret_response = request.form['g-recaptcha-response']

        verify_response = requests.post(url=f"{create_app().config['VERIFY_URL']}?secret={create_app().config['RECAPTCHA_SECRET_KEY']}&response={secret_response}").json()


        if verify_response['success'] == False or verify_response['score'] < 0.5:
            abort(401)

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
        elif len(email) < G_LEN_EMAIL or len(email) > NG_LEN_EMAIL:
            flash('Email ต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร', category='error')
        elif len(user_name) < G_LEN_UNAME or len(user_name) > NG_LEN_UNAME:
            flash('Username ต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร', category='error')
        elif len(first_name) < G_LEN_FNAME  or len(first_name) > NG_LEN_FNAME:
            flash('ชื่อจริงต้องมีขนาดตั้งแต่ 2 - 50 ตัวอักษร', category='error')
        elif len(last_name) < G_LEN_LNAME  or len(last_name) > NG_LEN_LNAME:
            flash('นามสกุลต้องมีขนาดตั้งแต่ 2 - 50 ตัวอักษร', category='error')
        elif password1 != password2:
            flash('กรุณาใส่ Password ให้ตรงกัน', category='error')
        elif len(password1) < G_LEN_PWORD or len(password1) > NG_LEN_PWORD:
            flash('Password ต้องมีขนาดตั้งแต่ 7 - 50 ตัวอักษร', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, user_name=user_name, password=generate_password_hash(password1, method='pbkdf2:sha256'), role_id=role_id)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')

            filename = None
            if 'profile_picture' in request.files:
                profile_picture = request.files['profile_picture']
            
                if profile_picture and allowed_file(profile_picture.filename):
                    filename = secure_filename(profile_picture.filename)
                    filename = f"{new_user.user_id}_profile.jpg"

                    file_path = os.path.join(PROFILE_FOLDER, filename)
                    profile_picture.save(file_path)
            
            new_user.profile_picture = filename
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('views_blueprint.home'))

    return render_template("sign_up.html", user=current_user, roles=sorted_roles, site_key=create_app().config['RECAPTCHA_SITE_KEY'])



@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        print(request.form)

        secret_response = request.form['g-recaptcha-response']

        verify_response = requests.post(url=f"{create_app().config['VERIFY_URL']}?secret={create_app().config['RECAPTCHA_SECRET_KEY']}&response={secret_response}").json()


        if verify_response['success'] == False or verify_response['score'] < 0.5:
            abort(401)

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

    return render_template("login.html", user=current_user, site_key=create_app().config['RECAPTCHA_SITE_KEY'])



@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_blueprint.login'))



# @auth_blueprint.route('/update-profile', methods=['POST'])
# @login_required
# def update_profile():
#     user = current_user

#     user_name = request.form.get('userName')
#     email = request.form.get('email')
#     first_name = request.form.get('firstName')
#     last_name = request.form.get('lastName')
#     role_id = request.form.get('role')
#     password = request.form.get('password')
#     new_password = request.form.get('newPassword')
#     confirm_new_password = request.form.get('confirmNewPassword')

#     can_update = True

#     if User.query.filter(User.email == email, User.user_id != user.user_id).first():
#         can_update = False
#         flash('Email นี้มีผู้ใช้แล้ว', category='error')
#     elif len(email) < G_LEN_EMAIL or len(email) > NG_LEN_EMAIL:
#         can_update = False
#         flash('Email ต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร', category='error')
#     elif len(first_name) < G_LEN_FNAME  or len(first_name) > NG_LEN_FNAME:
#         can_update = False
#         flash('ชื่อจริงต้องมีขนาดตั้งแต่ 2 - 50 ตัวอักษร', category='error')
#     elif len(last_name) < G_LEN_LNAME  or len(last_name) > NG_LEN_LNAME:
#         can_update = False
#         flash('นามสกุลต้องมีขนาดตั้งแต่ 2 - 50 ตัวอักษร', category='error')
#     elif User.query.filter(User.user_name == user_name, User.user_id != user.user_id).first():
#         can_update = False
#         flash('Username นี้มีผู้ใช้แล้ว', category='error')
#     elif len(user_name) < G_LEN_UNAME  or len(user_name) > NG_LEN_UNAME:
#         can_update = False
#         flash('ชื่อผู้ใช้ต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร', category='error')

#     # ตรวจสอบรหัสผ่านใหม่และการยืนยันรหัสผ่าน
#     # if new_password and confirm_new_password:
#     #     if new_password != confirm_new_password:
#     #         can_update = False
#     #         flash('รหัสผ่านใหม่และยืนยันรหัสผ่านไม่ตรงกัน', category='error')
#     #     elif len(new_password) < G_LEN_PWORD or len(new_password) > NG_LEN_PWORD:
#     #         can_update = False
#     #         flash('Password ต้องมีขนาดตั้งแต่ 7 - 50 ตัวอักษร', category='error')
#     if password:
#         if not check_password_hash(user.password, password):
#             can_update = False
#             flash('รหัสผ่านเดิมไม่ถูกต้อง', category='error')
#         elif new_password and confirm_new_password:
#             if new_password != confirm_new_password:
#                 can_update = False
#                 flash('รหัสผ่านใหม่และยืนยันรหัสผ่านไม่ตรงกัน', category='error')
#             elif len(new_password) < G_LEN_PWORD or len(new_password) > NG_LEN_PWORD:
#                 can_update = False
#                 flash('Password ต้องมีขนาดตั้งแต่ 7 - 50 ตัวอักษร', category='error')
#         else:
#             can_update = False
#             flash('กรุณากรอกรหัสผ่านใหม่และยืนยันรหัสผ่าน', category='error')

#     if can_update:
#         # อัปเดตข้อมูลในฐานข้อมูลเฉพาะเมื่อสามารถอัปเดตได้
#         user.user_name = user_name
#         user.first_name = first_name
#         user.last_name = last_name
#         user.email = email

#         if new_password:
#             # อัปเดตรหัสผ่านเฉพาะเมื่อมีการร้องขอเปลี่ยนแปลงรหัสผ่าน
#             user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

#         if role_id:
#             user.role_id = role_id

#         if 'profile_picture' in request.files:
#             # อัปโหลดรูปภาพโปรไฟล์เมื่อมีการอัปโหลดใหม่
#             profile_picture = request.files['profile_picture']
#             if profile_picture and allowed_file(profile_picture.filename):
#                 filename = secure_filename(profile_picture.filename)
#                 filename = f"{user.user_id}_profile.jpg"

#                 file_path = os.path.join(PROFILE_FOLDER, filename)

#                 if os.path.exists(file_path):
#                     os.remove(file_path)

#                 profile_picture.save(file_path)
#                 user.profile_picture = filename
        
#         db.session.commit()
#         flash('บันทึกข้อมูลสำเร็จ', category='success')

#     return redirect(url_for('views_blueprint.profile'))

@auth_blueprint.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    user = current_user

    user_name = request.form.get('userName')
    email = request.form.get('email')
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    role_id = request.form.get('role')
    password = request.form.get('password')
    new_password = request.form.get('newPassword')
    confirm_new_password = request.form.get('confirmNewPassword')

    errors = []

    if User.query.filter(User.email == email, User.user_id != user.user_id).first():
        errors.append('Email นี้มีผู้ใช้แล้ว')
    elif len(email) < G_LEN_EMAIL or len(email) > NG_LEN_EMAIL:
        errors.append('Email ต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร')
    elif len(first_name) < G_LEN_FNAME or len(first_name) > NG_LEN_FNAME:
        errors.append('ชื่อจริงต้องมีขนาดตั้งแต่ 2 - 50 ตัวอักษร')
    elif len(last_name) < G_LEN_LNAME or len(last_name) > NG_LEN_LNAME:
        errors.append('นามสกุลต้องมีขนาดตั้งแต่ 2 - 50 ตัวอักษร')
    elif User.query.filter(User.user_name == user_name, User.user_id != user.user_id).first():
        errors.append('Username นี้มีผู้ใช้แล้ว')
    elif len(user_name) < G_LEN_UNAME or len(user_name) > NG_LEN_UNAME:
        errors.append('ชื่อผู้ใช้ต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร')

    # ตรวจสอบรหัสผ่านใหม่และการยืนยันรหัสผ่าน
    if password:
        if not check_password_hash(user.password, password):
            errors.append('รหัสผ่านเดิมไม่ถูกต้อง')
        elif new_password and confirm_new_password:
            if new_password != confirm_new_password:
                errors.append('รหัสผ่านใหม่และยืนยันรหัสผ่านไม่ตรงกัน')
            elif len(new_password) < G_LEN_PWORD or len(new_password) > NG_LEN_PWORD:
                errors.append('Password ต้องมีขนาดตั้งแต่ 7 - 50 ตัวอักษร')
        else:
            errors.append('กรุณากรอกรหัสผ่านใหม่และยืนยันรหัสผ่าน')

    if errors:
        for error in errors:
            flash(error, category='error')
        return render_template('profile.html', user=user, roles=Role.query.all(), edit=True)
    
    # อัปเดตข้อมูลในฐานข้อมูลเฉพาะเมื่อสามารถอัปเดตได้
    user.user_name = user_name
    user.first_name = first_name
    user.last_name = last_name
    user.email = email

    if new_password:
        # อัปเดตรหัสผ่านเฉพาะเมื่อมีการร้องขอเปลี่ยนแปลงรหัสผ่าน
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

    if role_id:
        user.role_id = role_id

    if 'profile_picture' in request.files:
        # อัปโหลดรูปภาพโปรไฟล์เมื่อมีการอัปโหลดใหม่
        profile_picture = request.files['profile_picture']
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            filename = f"{user.user_id}_profile.jpg"

            file_path = os.path.join(PROFILE_FOLDER, filename)

            if os.path.exists(file_path):
                os.remove(file_path)

            profile_picture.save(file_path)
            user.profile_picture = filename
    
    db.session.commit()
    flash('บันทึกข้อมูลสำเร็จ', category='success')
    return redirect(url_for('views_blueprint.profile'))
