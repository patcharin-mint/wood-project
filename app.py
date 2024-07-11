from flask import Flask, render_template, request, flash, url_for, redirect, send_from_directory
from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, SelectField, StringField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
from keras.models import load_model
from keras.preprocessing import image
import os
import numpy as np
import pymysql


CLASS_NAMES = ['ching', 'euca', 'kapi', 'payung', 'pradu', 'sak', 'takian', 'teng', 'yangna', 'yangpara']
UPLOAD_FOLDER = 'static/images'


# รันด้วย module Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'KeY'

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='user',
    db='wood-identification-project'
)

# model = load_model('VGG16.keras')
model = load_model(r'VGG16.keras')

class PredictionForm(FlaskForm):
    # InputRequired() เป็นตัวตรวจสอบว่าฟิลด์ว่างเปล่าหรือไม่
    file = FileField("Photo", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')]
        )
    existing_source = SelectField("Choose an existing source", choices=[])
    new_source = StringField("Or enter a new source")

    submit = SubmitField("Check")


def get_sources(conn):
    with conn:
        cur = conn.cursor() 
        cur.execute('SELECT Source_name FROM woodSource')
        sources = cur.fetchall()
        return [source[0] for source in sources]



def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img = image.img_to_array(img)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)  # หรือใช้ img.reshape(1, 224, 224, 3)
    return img


def predictTopN(img_path, n):
	img = preprocess_image(img_path)

	preds = model.predict(img)

	top_indices = np.argsort(preds[0])[-n:][::-1]
	top_probabilities = preds[0][top_indices]

	print(top_indices)
	top_classes = [CLASS_NAMES[i] for i in top_indices]
	top_probabilities = [f"{prob * 100:.3f}%" for prob in top_probabilities]

	return dict(zip(top_classes, top_probabilities))


# routes
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/wood-identification", methods=['GET', 'POST'])
def prediction():

    form = PredictionForm()
    form.existing_source.choices = [(source, source) for source in get_sources(conn)]

    # กดปุ่ม submit = post
    if form.validate_on_submit():
        file = form.file.data

        selected_source = form.existing_source.data
        new_source = form.new_source.data.strip()

        if new_source:
            source = new_source
        else:
            source = selected_source

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # result prediction in form dictionary 
        pred = predictTopN(filepath, 5)
        print(pred)

        return render_template("predict.html", form=form, image_file=file.filename, predictions=pred, source=source)
    
    return render_template("predict.html", form=form)


# @app.route("/wood-identification", methods=['GET', 'POST'])
# def prediction():

#     form = PredictionForm()

#     # กดปุ่ม submit = post
#     if form.validate_on_submit():
#         file = form.file.data
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)

#         # result prediction in form dictionary 
#         pred = predictTopN(filepath, 5)
#         print(pred)

#         return render_template("predict.html", form=form, image_file=file.filename, predictions=pred)
    
#     return render_template("predict.html", form=form)



@app.route("/about")
def about():
    return render_template("about.html")

# use case
@app.route('/user/<name>')
def member(name):
     return f'<h1> hello {name} </h1>'


# สั่งรัน project / web server
if __name__ =='__main__':
	app.run(debug = True)
	
