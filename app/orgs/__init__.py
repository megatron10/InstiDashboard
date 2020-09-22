from flask import Blueprint
from flask_restful import Api
from app.gauth.routes import login_required

orgs_bp = Blueprint('orgs', __name__, url_prefix='/orgs')
orgs_api = Api(orgs_bp)


@orgs_bp.before_request
@login_required
def before_request():
    """ Protect all of the admin endpoints. """
    pass


from . import routes
