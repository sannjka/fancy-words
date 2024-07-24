from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
#from . import profile
from . import paint
from .. import db
from ..models import Phrase
#from .forms import UpdateAccountForm
#from .utils import save_picture
from .utils import get_figure_tag


@paint.route('/paint/<int:phrase_id>', methods=['GET', 'POST'])
#@login_required
def draw_svg(phrase_id):
    phrase = Phrase.query.get(phrase_id)
    image_file = url_for('static',
                     filename='phrase_pictures/' + phrase.image_file)
    return render_template('paint.html', title='Fancy-words-paint',
                           phrase=phrase, image_file=image_file)

@paint.route('/paint/get_figure', methods=['GET', 'POST'])
def get_figure():
    coordinates = request.args.get('coord')
    figure_tag = get_figure_tag(coordinates)
    #print('parameter', coordinates)
    return jsonify({'fig': figure_tag})
