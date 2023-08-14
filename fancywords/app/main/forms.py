from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class SearchForm(FlaskForm):
    search_field = StringField('Search')
    submit = SubmitField('Search')
