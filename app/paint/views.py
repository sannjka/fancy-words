import json
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import paint
from .. import db
from ..models import Phrase
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
    if request.is_json:
        coordinates = request.json
        print(type(coordinates))
        print('json', coordinates)
        x, y = coordinates['x'], coordinates['y']
    else:
        coordinates = request.args.get('coord')
        print('coord:', coordinates)
        json_coord = json.loads(coordinates)
        x, y = json_coord.get('x'), json_coord.get('y')
    figure_tag = get_figure_tag(x, y)
    return jsonify({'fig': figure_tag})
