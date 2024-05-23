from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .service.predService import predictTopN, CLASS_NAMES, PredictionForm, CLASS_NAMES_TH, createPredForm
from werkzeug.utils import secure_filename
import os
from . import db
from .models import Source


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


        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # result prediction in form dictionary 
        pred = predictTopN(filepath, 3)

        return render_template("predict.html", form=form, image_file=file.filename, predictions=pred, source=selected_source, user=current_user)
    else:
        print('not in post')
    return render_template("predict.html", form=form, user=current_user)




