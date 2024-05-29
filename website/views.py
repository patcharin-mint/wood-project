from flask import Blueprint, render_template, request, flash, redirect, abort, send_from_directory, url_for
from flask_login import login_required, current_user
from .service.predService import predictTopN, CLASS_NAMES, PredictionForm, CLASS_NAMES_TH, createPredForm
from werkzeug.utils import secure_filename
import os
from . import db, create_app
from .models import Source, PredictRecord, User, Wood, Role
import datetime
import locale
import requests


views_blueprint = Blueprint('views_blueprint', __name__)

UPLOAD_FOLDER = 'website/static/images'
STATIC_IMG_FOLDER = 'website/static/images'

# ตั้งค่า locale เป็น 'th_TH.UTF-8' เพื่อให้ Python รู้จักการเรียงลำดับภาษาไทย
locale.setlocale(locale.LC_COLLATE, 'th_TH.UTF-8')



# route

@views_blueprint.route('/', methods=['GET'])
def home():
    return render_template("home.html", user=current_user)





@views_blueprint.route('/wood-identification', methods=['GET', 'POST'])
def prediction():

    form = createPredForm()
    
    # กดปุ่ม submit = post
    if form.validate_on_submit():

        file = form.file.data
        selected_wood = form.existing_wood.data
        selected_source = form.existing_source.data
        new_source = form.new_source.data.strip()
        if new_source and len(new_source) < 4 or len(new_source) > 50:
            form.new_source.data = ''
            flash('ชื่อแหล่งที่มาต้องมีขนาดตั้งแต่ 4 - 50 ตัวอักษร', category='error')
        else:

            if current_user.is_authenticated:
                new_filename = f"{current_user.user_name}_predict_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%S')}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, new_filename)
                file.save(filepath)
            else:
                new_filename = "temp.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, new_filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                file.save(filepath)

            # ถ้า new_source มีค่า ให้เพิ่มลงในฐานข้อมูล
            if new_source and current_user.is_authenticated:
                existing_source = Source.query.filter_by(source_name=new_source).first()
                if not existing_source:
                    new_source_object = Source(source_name=new_source)
                    db.session.add(new_source_object)
                    db.session.commit()
                    selected_source = new_source_object.source_id

                    form = createPredForm()
            else:
                selected_source = int(selected_source)
            
            form.new_source.data = ''

            # result prediction in form dictionary 
            pred = predictTopN(filepath, 3)

            p1_wood = Wood.query.filter_by(wood_nickname=list(pred.keys())[0]).first()
            p2_wood = Wood.query.filter_by(wood_nickname=list(pred.keys())[1]).first()
            p3_wood = Wood.query.filter_by(wood_nickname=list(pred.keys())[2]).first()

            p1 = p1_wood.wood_name 
            p2 = p2_wood.wood_name
            p3 = p3_wood.wood_name 
            
            if current_user.is_authenticated:
                record = PredictRecord(
                    user_id=current_user.user_id,
                    date=datetime.datetime.now(),
                    user_role_id=current_user.role.role_id,
                    source_id=selected_source,
                    wood_id=selected_wood,
                    file_name=new_filename,
                    prob1=p1 + ' - ' + pred.get(list(pred.keys())[0]),
                    prob2=p2 + ' - ' + pred.get(list(pred.keys())[1]),
                    prob3=p3 + ' - ' + pred.get(list(pred.keys())[2])
                )
                db.session.add(record)
                db.session.commit()
            return render_template("predict.html", form=form, image_file=new_filename, predictions=pred, source=selected_source, user=current_user, site_key=create_app().config['RECAPTCHA_SITE_KEY'])
        
    return render_template("predict.html", form=form, user=current_user, site_key=create_app().config['RECAPTCHA_SITE_KEY'])



@views_blueprint.route('/prediction-history', methods=['GET', 'POST'])
@login_required
def prediction_history():

    sorted_sources = Source.query.order_by(Source.source_name).all()
    sorted_roles = Role.query.order_by(Role.role_name).all()
    sorted_woods = Wood.query.order_by(Wood.wood_name).all()

    prediction_history = PredictRecord.query.filter_by(user_id=current_user.user_id)
    prediction_history = prediction_history.order_by(PredictRecord.date.desc())


    if request.method == 'POST':

        search_source_query = request.form.get('search_source')
        search_role_query = request.form.get('search_role')
        search_wood_query = request.form.get('search_wood')

        if search_source_query:
            prediction_history = prediction_history.filter(PredictRecord.source_id == search_source_query)
        if search_role_query:
            prediction_history = prediction_history.filter(PredictRecord.user_role_id == search_role_query)
        if search_wood_query:
            prediction_history = prediction_history.filter(PredictRecord.wood_id == search_wood_query)

    return render_template("prediction_history.html", prediction_history=prediction_history, user=current_user, sources=sorted_sources, roles=sorted_roles, woods=sorted_woods)


@views_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':

        # กำหนด key ในการเรียงลำดับตามตัวอักษรภาษาไทย
        sorted_roles = sorted(Role.query.all(), key=lambda x: locale.strxfrm(x.role_name))

        return render_template("profile.html", user=current_user, edit=True, roles=sorted_roles)
    return render_template("profile.html", user=current_user, edit=False)



@views_blueprint.route('/woods-info', methods=['GET', 'POST'])
def woods_info():
    request.form.getlist('compare_woods')
    search_query = request.form.get('search', '')

    if search_query:
        sorted_woods = sorted(Wood.query.filter(Wood.wood_name.ilike(f'%{search_query}%')).all(), key=lambda x: locale.strxfrm(x.wood_name))
    else:
        sorted_woods = sorted(Wood.query.all(), key=lambda x: locale.strxfrm(x.wood_name))
    return render_template("woods_info.html", user=current_user, woods=sorted_woods)



@views_blueprint.route('/woods-info/<int:wood_id>')
def wood_detail(wood_id):
    # ถ้าไม่มีข้อมูลที่ตรงกันในฐานข้อมูล จะส่ง HTTP 404 error response โดยอัตโนมัติ
    wood = Wood.query.get_or_404(wood_id)
    return render_template('wood_detail.html', wood=wood, user=current_user)


@views_blueprint.route('/compare-woods', methods=['POST'])
def compare_woods():
    wood_ids = request.form.getlist('compare_woods')

    if len(wood_ids) < 2:
        flash('Please select at least two types of wood to compare.', 'error')
        return redirect(url_for('views_blueprint.woods_info'))

    woods = Wood.query.filter(Wood.wood_id.in_(wood_ids)).all()

    return render_template("compare_woods.html", woods=woods, user=current_user)




@views_blueprint.route('/admin_mangement')
@login_required
def management():
    return render_template("admin_mangement.html", user=current_user)



