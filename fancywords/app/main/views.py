from collections import namedtuple
from itertools import chain
from flask import (render_template, redirect, url_for, flash, request,
                   current_app)
from flask_login import current_user, login_required
from . import main
from .. import db
from ..models import Phrase, Comment, Example, WordList, User
from .forms import (SearchForm, CommentForm, EditPhraseForm, AddExampleForm,
                    SelectExampleForm, AddWordListForm)
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
                           title=title, word=word, pagination=None,
                           next=request.url)

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
@main.route('/add_phrase/', methods=['GET', 'POST'])
@login_required
def add_phrase(word=''):
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
        next = request.args.get('next')
        if next is None:
            next = url_for('main.phrase_map', phrase_id=phrase.id)
        return redirect(next)
    form.body.data = word
    image_file = url_for('static',
                     filename='phrase_pictures/default.jpg')
    return render_template('edit_phrase.html', form=form, phrase=None,
                           image_file=image_file, title='Create phrase')

@main.route('/phrases/<wordlist_id>')
@main.route('/phrases')
@login_required
def phrases(wordlist_id=None):
    if wordlist_id:
        wordlist = WordList.query.get_or_404(wordlist_id)
        query = wordlist.phrases
        title = wordlist.title
    else:
        query = Phrase.query.filter_by(author=current_user)
        title = 'My phrases'
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Phrase.body).paginate(
        page=page, per_page=current_app.config['PHRASES_PER_PAGE'],
        error_out=False)
    phrases = pagination.items
    return render_template('index.html', phrases=phrases, word = '',
                           pagination=pagination, title=title,
                           next=request.url)

@main.route('/wordlists/<int:user_id>')
@main.route('/wordlists')
@login_required
def wordlists(user_id=None):
    if user_id:
        user = User.query.get_or_404(user_id)
        query = WordList.query.filter_by(author=user)
        if user_id == current_user.id:
            title = 'My wordlists:'
        else:
            title = user.username + "'s wordlistst:"
        show_all = False
    else:
        query = WordList.query
        title = 'Wordlists:'
        show_all = True
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(WordList.title).paginate(
        page=page, per_page=current_app.config['WORDLISTS_PER_PAGE'],
        error_out=False)
    wordlists = pagination.items
    return render_template('wordlists.html', wordlists=wordlists,
                           pagination=pagination, title=title,
                           show_all=show_all, next=request.url,
                           user_id=user_id)

@main.route('/wordlist', methods=['GET', 'POST'])
@login_required
def wordlist():
    wl_id = request.args.get('wl_id')
    fill = request.args.get('fill', 'false')
    word = request.args.get('word', '')
    page = request.args.get('page', 1, type=int)
    wordlist = WordList.query.get_or_404(wl_id)
    pagination = wordlist.phrases.order_by(Phrase.body).paginate(
        page=page, per_page=current_app.config['PHRASES_PER_PAGE'],
        error_out=False)
    phrases = pagination.items
    image_file = url_for('static',
                     filename='profile_pictures/' + current_user.avatar_file)
    form = None
    found_phrases = None
    if fill == 'true':
        form = SearchForm()
        if form.validate_on_submit():
            word = form.search_field.data
            if word:
                return redirect(url_for('main.wordlist', wl_id=wl_id,
                                        fill=fill, word=word))
            else:
                return redirect(url_for('main.wordlist', wl_id=wl_id,
                                        fill=fill))
        form.search_field.data = word
        if word:
            found_phrases = Phrase.find_phrase(word)
    return render_template('wordlist.html', wordlist=wordlist,
                           phrases=phrases, pagination=pagination,
                           image_file=image_file, fill=fill, form=form,
                           found_phrases=found_phrases, next=request.url)

@main.route('/add_wordlist/<int:wl_id>', methods=['GET', 'POST'])
@main.route('/add_wordlist', methods=['GET', 'POST'])
@login_required
def add_update_wordlist(wl_id=None):
    form = AddWordListForm()
    wordlist = None
    title = 'Create wordlist'
    if wl_id:
        wordlist = WordList.query.get(wl_id)
        title = 'Update wordlist'
    if form.validate_on_submit():
        if not wordlist:
            wordlist = WordList(author=current_user._get_current_object())
            db.session.add(wordlist)
        wordlist.title = form.title.data
        db.session.commit()
        next = request.args.get('next')
        if next is None:
            next = url_for('main.wordlist', wl_id=wordlist.id)
        return redirect(next)
    if wordlist:
        form.title.data = wordlist.title
    return render_template('edit_wordlist.html', form=form, title=title)

@main.route('/add_to_wordlist')
@login_required
def add_to_wordlist():
    phrase_id = request.args.get('phrase_id')
    wl_id = request.args.get('wl_id')
    if phrase_id and wl_id:
        phrase = Phrase.query.get_or_404(phrase_id)
        wordlist = WordList.query.get_or_404(wl_id)
        wordlist.add_phrase(phrase)
    return redirect(request.args.get('next'))

@main.route('/remove_from_wordlist')
@login_required
def remove_from_wordlist():
    phrase_id = request.args.get('phrase_id')
    wl_id = request.args.get('wl_id')
    if phrase_id and wl_id:
        phrase = Phrase.query.get_or_404(phrase_id)
        wordlist = WordList.query.get_or_404(wl_id)
        wordlist.remove_phrase(phrase)
    return redirect(request.args.get('next'))

