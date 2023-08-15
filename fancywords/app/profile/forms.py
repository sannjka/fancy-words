from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from ..models import User


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture',
                        validators=[FileAllowed(['jpg', 'jpeg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username).first()
            if user:
                raise ValidationError('That username is taken')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(username=username).first()
            if user:
                raise ValidationError('That email is taken')
