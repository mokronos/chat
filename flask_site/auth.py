from flask import (
        render_template, redirect, url_for, request, Blueprint, flash, session, g, Response
        )

from werkzeug.security import generate_password_hash, check_password_hash

import functools
import json

from .db import get_db
from .htmx import htmx
from .utils.helpers import htmx_required, htmx_redirect
from .forms import LoginForm, RegisterForm
from flask_wtf import FlaskForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
@htmx_required
def register():

    form = RegisterForm()

    if request.method == 'POST':

        if not form.validate():

            # bad request
            return {'template': 'auth/register.html', 'context':{'form': form}, 'code': 400}

        username = form.username.data
        # password2 equality already validated by form
        password = form.password.data

        db = get_db()

        try:
            db.execute(
                    'INSERT INTO user (username, password) VALUES (?, ?)',
                    (username, generate_password_hash(password))
                    )
            db.commit()
            resp = Response()
            resp.headers['HX-Location'] = json.dumps({'path': url_for('auth.login'), 'target': '#main', 'source': '#htmx-location-source'})
            # no content to send on successful registration
            resp.status_code = 204
            return resp
        except db.IntegrityError:
            error = f"Username {username} is not available anymore."
            form.username.errors += (error,)

            # conflict with server state
            return {'template': 'auth/register.html', 'context':{'form': form}, 'code': 409}



    return {'template': 'auth/register.html', 'context':{'form': form}}

@bp.route('/login', methods=('GET', 'POST'))
@htmx_required
def login():

    form = LoginForm()

    if request.method == 'POST':

        if not form.validate():

            # bad request
            return {'template': 'auth/login.html', 'context':{'form': form}, 'code': 400}

        username = form.username.data
        password = form.password.data

        db = get_db()
        user = db.execute(
                'SELECT password, id FROM user WHERE username = ?', (username,)
                ).fetchone()

        if user and check_password_hash(user['password'], password):

                session.clear()
                session['user_id'] = user['id']

                resp = Response()
                resp.headers['HX-Trigger'] = 'auth-status-changed'
                resp.headers['HX-Location'] = json.dumps({'path': url_for('argue.overview'), 'target': '#main', 'source': '#htmx-location-source'})
                # no content to send on successful login
                resp.status_code = 204
                return resp

        error = 'Incorrect username or password.'
        form.username.errors += (error,)
        form.password.errors += (error,)

        return {'template': 'auth/login.html', 'context':{'form': form}, 'code': 401}


    return {'template': 'auth/login.html', 'context':{'form': form}}


@bp.route('/logout', methods=('POST',))
def logout():

    # just for csrf validation
    form = FlaskForm()
    if form.validate():
        session.clear()
        resp = Response()
        resp.headers['HX-Trigger'] = 'auth-status-changed'
        resp.headers['HX-Location'] = json.dumps({'path': url_for('argue.overview'), 'target': '#main', 'source': '#htmx-location-source'})
        return resp

    # this is never reached i think, but i want it to
    resp = Response()
    resp.status_code = 401
    # something went bad or somebody is trying weird stuff
    # refresh page to renew the csrf token
    resp.headers['HX-Refresh'] = 'true'
    return resp


@bp.route('/status', methods=('GET',))
def status():
    return render_template('basics/auth_bar.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
                ).fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('You must be logged in to view this page.')
            return htmx_redirect('auth.login', flash=True)

        return view(**kwargs)

    return wrapped_view
