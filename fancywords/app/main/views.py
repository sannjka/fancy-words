from flask import render_template
from . import main
from ..models import Phrase
from .forms import SearchForm

@main.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    phrase = Phrase.randome_phrase()
    return render_template('index.html', phrase=phrase, form=form)
