from flask import render_template, redirect, url_for, flash
from . import main
from ..models import Phrase
from .forms import SearchForm

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
                           title=title)

