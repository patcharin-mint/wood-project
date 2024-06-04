from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class RoleForm(FlaskForm):
    role_name = StringField('Role Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class WoodForm(FlaskForm):
    wood_name = StringField('Wood Name', validators=[DataRequired()])
    wood_nickname = StringField('Wood Nickname', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SourceForm(FlaskForm):
    source_name = StringField('Source Name', validators=[DataRequired()])
    submit = SubmitField('Submit')
