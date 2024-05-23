from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, SelectField, StringField
from flask_wtf.file import FileAllowed, FileRequired
from ..models import Source


CLASS_NAMES = ['ching', 'euca', 'kapi', 'payung', 'pradu', 'sak', 'takian', 'teng', 'yangna', 'yangpara']
CLASS_NAMES_TH = ['ชิงชัน', 'ยูคาลิปตัส', 'กะพี้เขาควาย', 'พะยูง', 'ประดู่', 'สัก', 'ตะเคียน', 'เต็ง', 'ยางนา', 'ยางพารา']
model = load_model(r'C:\Users\user\Downloads\project_new\wood-project_v3\no-non\VGG19.keras')



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
	top_probabilities = [f"{prob * 100:.2f}%" for prob in top_probabilities]

	return dict(zip(top_classes, top_probabilities))


# class PredictionForm(FlaskForm):
#     # InputRequired() เป็นตัวตรวจสอบว่าฟิลด์ว่างเปล่าหรือไม่
#     file = FileField("Photo", validators=[
#         FileRequired(),
#         FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')]
#         )
#         # ฟิลด์การเลือกพันธุ์ไม้
#     class_name = SelectField('Choose the wood species', choices=[(name, name) for name in CLASS_NAMES_TH])
#     source = SelectField("Select Source", choices=[], coerce=int, render_kw={"id": "source"})
#     new_source = StringField("New Source (if not in list)")
#     submit = SubmitField("Upload File")


class PredictionForm(FlaskForm):
    # InputRequired() เป็นตัวตรวจสอบว่าฟิลด์ว่างเปล่าหรือไม่
    file = FileField("Photo", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')]
        )
    
    existing_wood = SelectField('Choose the wood species', choices=[])
    existing_source = SelectField("Choose an existing source", choices=[])
    new_source = StringField("Or enter a new source")
    submit = SubmitField("Predict")



def createPredForm():
    form = PredictionForm()

    sources = [(source.source_id, source.source_name) for source in Source.query.all()]
    print(sources)
    form.existing_source.choices = sources
    form.existing_wood.choices = [(wood, wood) for wood in CLASS_NAMES_TH]

    return form


