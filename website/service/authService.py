from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf import FlaskForm
from ..models import Role
from flask_wtf.file import FileField, FileAllowed


class SignUpForm(FlaskForm):
    email = StringField('อีเมล', validators=[DataRequired(), Email(), Length(min=4)])
    first_name = StringField('ชื่อจริง', validators=[DataRequired(), Length(min=2)])
    last_name = StringField('นามสกุล', validators=[DataRequired(), Length(min=2)])
    user_name = StringField('ชื่อผู้ใช้', validators=[DataRequired(), Length(min=2)])
    password1 = PasswordField('รหัสผ่าน', validators=[DataRequired(), Length(min=7)])
    password2 = PasswordField('ยืนยันรหัสผ่าน', validators=[DataRequired(), EqualTo('password1')])
    role = SelectField('บทบาท', validators=[DataRequired()], coerce=int)
    profile_picture = FileField('รูปภาพโปรไฟล์', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('ลงทะเบียน')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.role_id, role.role_name) for role in Role.query.all()]