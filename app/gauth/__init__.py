from flask import Blueprint
from flask_restful import Api

gauth_bp = Blueprint('gauth', __name__, url_prefix='/auth')

from . import routes