from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .service.predService import predictTopN, CLASS_NAMES, PredictionForm, CLASS_NAMES_TH, createPredForm
from werkzeug.utils import secure_filename
import os
from . import db
from .models import Source, PredictRecord, User, Wood
import datetime


views_blueprint = Blueprint('views_blueprint', __name__)

UPLOAD_FOLDER = 'website/static/images'

@views_blueprint.route('/', methods=['GET'])
@login_required
def home():
    return render_template("home.html", user=current_user)


@views_blueprint.route('/wood-identification', methods=['GET', 'POST'])
@login_required
def prediction():

    form = createPredForm()

    # กดปุ่ม submit = post
    if form.validate_on_submit():
        file = form.file.data

        selected_wood = form.existing_wood.data
        print('selected wood')
        print(selected_wood)
        wood = Wood.query.get(selected_wood)
        print("The name of the selected wood is:", wood.wood_name)


        selected_source = form.existing_source.data
        new_source = form.new_source.data.strip()

        # ถ้า new_source มีค่า ให้เพิ่มลงในฐานข้อมูล
        if new_source:
            existing_source = Source.query.filter_by(source_name=new_source).first()
            if not existing_source:
                new_source_object = Source(source_name=new_source)
                db.session.add(new_source_object)
                db.session.commit()
                selected_source = new_source_object.source_id

                form = createPredForm()
        else:
            selected_source = int(selected_source)

        new_filename = f"{current_user.user_name}_predict_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(filepath)
        
        # result prediction in form dictionary 
        pred = predictTopN(filepath, 3)

        p1_wood = Wood.query.filter_by(wood_nickname=list(pred.keys())[0]).first()
        p2_wood = Wood.query.filter_by(wood_nickname=list(pred.keys())[1]).first()
        p3_wood = Wood.query.filter_by(wood_nickname=list(pred.keys())[2]).first()

        p1 = p1_wood.wood_name 
        p2 = p2_wood.wood_name
        p3 = p3_wood.wood_name 

        record = PredictRecord(user_id=current_user.user_id,
                               source_id=selected_source,
                               wood_id = selected_wood,
                               file_name=new_filename,
                               prob1= p1 + ' - ' + pred.get(list(pred.keys())[0]),
                               prob2= p2 + ' - ' + pred.get(list(pred.keys())[1]),
                               prob3= p3 + ' - ' + pred.get(list(pred.keys())[2]))
        db.session.add(record)
        db.session.commit()

        return render_template("predict.html", form=form, image_file=new_filename, predictions=pred, source=selected_source, user=current_user)
    else:
        print('not in post')
    return render_template("predict.html", form=form, user=current_user)



@views_blueprint.route('/prediction-history')
@login_required
def prediction_history():
    prediction_history = PredictRecord.query.filter_by(user_id=current_user.user_id).all()
    return render_template("prediction_history.html", prediction_history=prediction_history, user=current_user)



@views_blueprint.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)
