# ourapp/forms.py

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

class EmailPasswordForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
