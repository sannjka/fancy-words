from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField,
                     SelectField)
from wtforms.validators import DataRequired, Regexp

class SearchForm(FlaskForm):
    search_field = StringField('')
    submit = SubmitField('Search')

class EditPhraseForm(FlaskForm):
    body = StringField('Phrase', validators=[DataRequired(),
                                             Regexp('[A-Za-z\s-]*')])
    transcription = StringField('Transcription')
    meaning = StringField('Meaning')
    translation = StringField('Translation', validators=[DataRequired()])
    picture = FileField('Update Picture',
                        validators=[FileAllowed(['jpg', 'jpeg','png'])])
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})

class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditExampleForm(FlaskForm):
    example = TextAreaField('', validators=[Regexp('[A-Za-z\s-]*')])
    submit = SubmitField('Save')

class SelectExampleForm(FlaskForm):
    select = SelectField('', validate_choice=False)
    example = TextAreaField('', validators=[Regexp('[A-Za-z\s-]*')])
    submit = SubmitField('Add')

class AddWordListForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(),
                                             Regexp('[A-Za-z\s-]*')])
    submit = SubmitField('Save')
