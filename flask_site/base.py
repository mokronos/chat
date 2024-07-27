from flask import render_template, redirect, url_for, request, Blueprint

from .auth import login_required
from .utils.helpers import htmx_required

# bp = Blueprint('base', __name__, url_prefix='/aw')
from .argue import bp

@bp.route('/index')
def index():
    resp = redirect(url_for('argue.overview'), code=303)
    resp.headers['HX-Trigger'] = 'auth-status-changed'
    return resp

@bp.route('/about')
@htmx_required
def about():
    return 'basics/about.html'
