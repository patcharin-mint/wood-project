from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, SelectField, StringField
from flask_wtf.file import FileAllowed, FileRequired
from ..models import Source, Wood
import locale


CLASS_NAMES = ['ching', 'euca', 'kapi', 'payung', 'pradu', 'sak', 'takian', 'teng', 'yangna', 'yangpara']
CLASS_NAMES_TH = ['ชิงชัน (Dalbergia oliveri)', 'ยูคาลิปตัส (Eucalyptus globulus)', 'กะพี้เขาควาย (Dalbergia cultrata Graham ex Benth.)', 'พะยูง (Dalbergia cochinchinensis)', 'ประดู่ (Pterocarpus macrocarpus)', 'สัก (Tectona grandis)', 'ตะเคียน (Hopea odorata)', 'เต็ง (Shorea obtusa Wall)', 'ยางนา (Dipterocarpus alatus)', 'ยางพารา (Hevea brasiliensis)']

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

    # ตั้งค่า locale เป็น 'th_TH.UTF-8' เพื่อให้ Python รู้จักการเรียงลำดับภาษาไทย
    locale.setlocale(locale.LC_COLLATE, 'th_TH.UTF-8')

    # กำหนด key ในการเรียงลำดับตามตัวอักษรภาษาไทย
    sorted_sources = sorted(Source.query.all(), key=lambda x: locale.strxfrm(x.source_name))
    sorted_woods = sorted(Wood.query.all(), key=lambda x: locale.strxfrm(x.wood_name))

    form.existing_source.choices = [(source.source_id, source.source_name) for source in sorted_sources]
    form.existing_wood.choices = [(wood.wood_id, wood.wood_name) for wood in sorted_woods]

    return form


