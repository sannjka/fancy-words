from flask import Blueprint

paint = Blueprint('paint', __name__)

from . import views
