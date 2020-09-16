from flask import Blueprint
from flask_restful import Api

orgs_bp = Blueprint('orgs', __name__, url_prefix='/orgs')
orgs_api = Api(orgs_bp)
from . import routes
