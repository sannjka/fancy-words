from collections import namedtuple
from itertools import chain
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from . import main
from .. import db
from ..models import Phrase, Comment, Example
from .forms import (SearchForm, CommentForm, EditPhraseForm, AddExampleForm,
                    SelectExampleForm)
from ..profile.utils import save_picture

@main.route('/', methods=['GET', 'POST'])
@main.route('/phrase/<word>', methods=['GET', 'POST'])
def index(word=''):
    form = SearchForm()
    if form.validate_on_submit():
        word = form.search_field.data
        if word:
            return redirect(url_for('main.index', word=word))
        else:
            return redirect(url_for('main.index'))
    form.search_field.data = word
    if word:
        phrases = Phrase.find_phrase(word)
        title = None
    else:
        phrases = [Phrase.randome_phrase()]
        title = 'Arbitrarily selected phrase:'
    if not phrases:
        flash('Nothing found', 'danger')
    return render_template('index.html', phrases=phrases, form_search=form,
                           title=title, word=word)

@main.route('/phrase_map/<int:phrase_id>', methods=['GET', 'POST'])
def phrase_map(phrase_id):
    phrase = Phrase.query.get(phrase_id)
    if not phrase:
        return redirect(url_for('main.index'))
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment = Comment(body=comment_form.body.data,
                          phrase=phrase,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.', 'success')
        return redirect(url_for('main.phrase_map', phrase_id=phrase_id))
    return render_template('phrase_map.html', phrase=phrase,
                           wordlists=phrase.wordlists.all(),
                           examples=phrase.examples.all(),
                           comments=phrase.comments.all(),
                           comment_form=comment_form)

@main.route('/edit_phrase/<int:phrase_id>', methods=['GET', 'POST'])
@login_required
def edit_phrase(phrase_id):
    phrase = Phrase.query.get(phrase_id)
    if not phrase:
        return redirect(url_for('main.index'))
    form = EditPhraseForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'phrase_pictures')
            phrase.image_file = picture_file
        phrase.body = form.body.data
        phrase.transcription = form.transcription.data
        phrase.translation = form.translation.data
        phrase.meaning = form.meaning.data
        db.session.commit()
        return redirect(url_for('main.phrase_map', phrase_id=phrase.id))
    form.body.data = phrase.body
    form.transcription.data = phrase.transcription
    form.translation.data = phrase.translation
    form.meaning.data = phrase.meaning
    image_file = url_for('static',
                     filename='phrase_pictures/' + phrase.image_file)
    return render_template('edit_phrase.html', form=form, phrase=phrase,
                           image_file=image_file)

@main.route('/add_example/<int:phrase_id>', methods=['GET', 'POST'])
@login_required
def add_example(phrase_id):
    phrase = Phrase.query.get(phrase_id)
    if not phrase:
        return redirect(url_for('main.index'))
    suggestions = Example.get_relevant_examples(phrase)
    if suggestions:
        Record = namedtuple('Record', 'id body')
        form = SelectExampleForm()
        form.select.choices = [(s.id, s.body)
            for s in chain([Record(None, '')], suggestions)]
    else:
        form = AddExampleForm()
    if form.validate_on_submit():
        if form.example.data:
            example = Example(body=form.example.data)
            db.session.add(example)
            db.session.commit()
            phrase.add_example(example)
        if suggestions:
            example = Example.query.get(form.select.data)
            if example:
                phrase.add_example(example)
        return redirect(url_for('main.phrase_map', phrase_id=phrase_id))
    return render_template('add_example.html', form=form, phrase=phrase,
                           suggestions=suggestions)

@main.route('/add_phrase/<word>', methods=['GET', 'POST'])
@login_required
def add_phrase(word):
    form = EditPhraseForm()
    if form.validate_on_submit():
        phrase = Phrase(body=form.body.data,
                        transcription=form.transcription.data,
                        translation=form.translation.data,
                        meaning=form.meaning.data,
                        author=current_user._get_current_object())
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'phrase_pictures')
            phrase.image_file = picture_file
        db.session.add(phrase)
        db.session.commit()
        return redirect(url_for('main.phrase_map', phrase_id=phrase.id))
    form.body.data = word
    image_file = url_for('static',
                     filename='phrase_pictures/default.jpg')
    return render_template('edit_phrase.html', form=form, phrase=None,
                           image_file=image_file, title='Create phrase')
