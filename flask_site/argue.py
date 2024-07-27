from flask import ( render_template, url_for, request,
                   Blueprint, g, flash, Response)

from .forms import ConnectionForm, ArgumentForm, PremiseForm, ConclusionForm
from .db import get_db
from .htmx import htmx

from .auth import login_required
from .utils import data
from .utils.helpers import htmx_required, htmx_redirect

import json

bp = Blueprint('argue', __name__, url_prefix='/')

@bp.route('/', methods=('GET',))
@htmx_required
def overview():

    db = get_db()
    arguments = db.execute((
            'SELECT argument.*, user.username '
            'FROM argument JOIN user ON argument.user_id = user.id '
            'ORDER BY created DESC'),
            ()
            ).fetchall()

    # get list of all the premises ids of each argument
    # there might be a better way to do this, via a join or something
    arguments_premises = dict()
    arguments_conclusions = dict()
    for argument in arguments:
        prems = db.execute(
                'SELECT id,title,content FROM argument_premise INNER JOIN premise ON argument_premise.premise_id = premise.id WHERE argument_premise.argument_id = ?',
                (argument['id'],)
                ).fetchall()
        arguments_premises[argument['id']] = prems
        concs = db.execute(
                'SELECT id,title,content FROM argument_conclusion INNER JOIN conclusion ON argument_conclusion.conclusion_id = conclusion.id WHERE argument_conclusion.argument_id = ?',
                (argument['id'],)
                ).fetchall()
        arguments_conclusions[argument['id']] = concs

    return {'template': 'argue/overview.html',
            'context': {'arguments': arguments, 'arguments_premises': arguments_premises, 'arguments_conclusions': arguments_conclusions}}



@bp.route('/search', methods=('GET',))
@htmx_required
def search():

    items = data.get_all(request)
    return {'template':'argue/search.html', 'context': {'items': items}}


@bp.route('/arguments/create', methods=('GET', 'POST'))
@htmx_required
@login_required
def arguments_create():

    form = ArgumentForm()

    if request.method == 'POST':

        if not form.validate():
            # bad request
            return {'template': 'argue/arguments_create.html', 'context':{'form': form}, 'code': 400}

        title = form.title.data
        content = form.content.data

        db = get_db()

        try:
            row = db.execute(
                    'INSERT INTO argument (title, content, user_id) VALUES (?, ?, ?)',
                    (title, content, g.user['id'])
                    )
            db.commit()
            resp = Response()
            resp.headers['HX-Location'] = json.dumps({'path': url_for('argue.overview'), 'target': '#main', 'source': '#htmx-location-source'})
            # no content to send on successful registration
            resp.status_code = 204
            return resp

        except db.IntegrityError:

            # conflict with server state
            return {'template': 'argue/arguments_create.html', 'context':{'form': form}, 'code': 409}


    return {'template': 'argue/arguments_create.html', 'context':{'form': form}}


@bp.route('/premises/create', methods=('GET', 'POST'))
@htmx_required
@login_required
def premises_create():

    form = PremiseForm()

    arguments = data.fetch_items_for_user('argument')

    form.argument.choices = [(-1, 'None')] + [
    (argument['id'], f"{argument['id']}| {argument['title']}") for argument in arguments
    ]

    if request.method == 'POST':

        if not form.validate():
            # bad request
            return {'template': 'argue/premises_create.html', 'context':{'form': form}, 'code': 400}
        title = form.title.data
        content = form.content.data
        argument_id = form.argument.data

        db = get_db()

        try:
            cur = db.execute(
                    'INSERT INTO premise (title, content, user_id) VALUES (?, ?, ?)',
                    (title, content, g.user['id'])
                    )
            if argument_id != -1:
                db.execute(
                        'INSERT INTO argument_premise (argument_id, premise_id) VALUES (?, ?)',
                        (argument_id, cur.lastrowid)
                        )
            db.commit()
            resp = Response()
            resp.headers['HX-Location'] = json.dumps({'path': url_for('argue.overview'), 'target': '#main', 'source': '#htmx-location-source'})
            # no content to send on successful registration
            resp.status_code = 204
            return resp
        except db.IntegrityError:
            # conflict with server state
            return {'template': 'argue/premises_create.html', 'context':{'form': form}, 'code': 409}

    return {'template': 'argue/premises_create.html', 'context': {'form': form}}

@bp.route('/conclusions/create', methods=('GET', 'POST'))
@htmx_required
@login_required
def conclusions_create():

    form = ConclusionForm()

    db = get_db()

    arguments = data.fetch_items_for_user('argument')

    form.argument.choices = [(-1, 'None')] + [
    (argument['id'], f"{argument['id']}| {argument['title']}") for argument in arguments
    ]

    if request.method == 'POST':

        if not form.validate():
            # bad request
            return {'template': 'argue/conclusions_create.html', 'context':{'form': form}, 'code': 400}

        title = form.title.data
        content = form.content.data
        argument_id = form.argument.data

        try:
            cur = db.execute(
                    'INSERT INTO conclusion (title, content, user_id) VALUES (?, ?, ?)',
                    (title, content, g.user['id'])
                    )
            if argument_id != -1:
                db.execute(
                        'INSERT INTO argument_conclusion (argument_id, conclusion_id) VALUES (?, ?)',
                        (argument_id, cur.lastrowid)
                        )
            db.commit()
            return htmx_redirect('argue.overview')

        except db.IntegrityError:
            # conflict with server state
            return {'template': 'argue/conclusions_create.html', 'context':{'form': form}, 'code': 409}

    return {'template': 'argue/conclusions_create.html', 'context': {'form': form}}


@bp.route('/arguments/<int:id>/delete', methods=('DELETE',))
@login_required
def arguments_delete(id):
    db = get_db()

    check = None
    check = db.execute('DELETE FROM argument WHERE id = ? AND user_id = ?', (id, g.user['id']))

    if check and check.rowcount == 0:
        flash("You don't have permission to delete this item")
        return "", 403
    db.commit()
    return "", 200


@bp.route('/premises/<int:id>/delete', methods=('DELETE',))
@login_required
def premises_delete(id):
    db = get_db()

    check = None
    check = db.execute('DELETE FROM premise WHERE id = ? AND user_id = ?', (id, g.user['id']))

    if check and check.rowcount == 0:
        flash("You don't have permission to delete this item")
        return "", 403
    db.commit()
    return "", 200


@bp.route('/conclusions/<int:id>/delete', methods=('DELETE',))
@login_required
def conclusions_delete(id):
    db = get_db()

    check = None
    check = db.execute('DELETE FROM conclusion WHERE id = ? AND user_id = ?', (id, g.user['id']))

    if check and check.rowcount == 0:
        flash("You don't have permission to delete this item")
        return "", 403
    db.commit()
    return "", 200

@bp.route('arguments/<int:id>', methods=('GET',))
@htmx_required
def arguments_details(id):

    db = get_db()

    item = db.execute(
            "SELECT * FROM argument WHERE id = ?",
            (id,)
            ).fetchone()

    if not item:
        flash("Requested item does not exist (anymore?)")
        return htmx_redirect('argue.search', flash=True)

    return {'template': 'argue/details.html', 'context': {'item': item, 'category': 'argument'}}


@bp.route('premises/<int:id>', methods=('GET',))
@htmx_required
def premises_details(id):

    db = get_db()

    item = db.execute(
            "SELECT * FROM premise WHERE id = ?",
            (id,)
            ).fetchone()

    if not item:
        flash("Requested item does not exist (anymore?)")
        return htmx_redirect('argue.search', flash=True)

    return {'template': 'argue/details.html', 'context': {'item': item, 'category': 'premise'}}


@bp.route('conclusions/<int:id>', methods=('GET',))
@htmx_required
def conclusions_details(id):

    db = get_db()

    item = db.execute(
            "SELECT * FROM conclusion WHERE id = ?",
            (id,)
            ).fetchone()

    if not item:
        flash("Requested item does not exist (anymore?)")
        return htmx_redirect('argue.search', flash=True)

    return {'template': 'argue/details.html', 'context': {'item': item, 'category': 'conclusion'}}
    
@bp.route('arguments/<int:id>/edit', methods=('GET', 'PUT'))
@htmx_required
@login_required
def arguments_edit(id):

    form = ArgumentForm()

    db = get_db()

    if request.method == 'PUT':
        if not form.validate():
            # bad request
            return {'template': 'argue/arguments_edit.html', 'context':{'form': form}, 'code': 400}

        title = form.title.data
        content = form.content.data

        db.execute(
            "UPDATE argument SET title = ?, content = ? WHERE id = ?",
            (title, content, id)
            )
        db.commit()
        resp = Response()
        resp.headers['HX-Location'] = json.dumps({'path': url_for('argue.arguments_details', id=id),
                                                  'target': '#main', 'source': '#htmx-location-source'})
        # no content to send on successful registration
        resp.status_code = 204
        return resp

    item = db.execute(
            "SELECT * FROM argument WHERE id = ?",
            (id,)
            ).fetchone()

    form.title.data = item['title']
    form.content.data = item['content']

    return {'template': 'argue/arguments_edit.html', 'context': {'form': form, 'id': id}}

@bp.route('premises/<int:id>/edit', methods=('GET', 'PUT'))
@htmx_required
@login_required
def premises_edit(id):

    form = PremiseForm()

    db = get_db()

    if request.method == 'PUT':
        if not form.validate():
            # bad request
            return {'template': 'argue/premises_edit.html', 'context':{'form': form}, 'code': 400}

        title = form.title.data
        content = form.content.data

        db.execute(
            "UPDATE premise SET title = ?, content = ? WHERE id = ?",
            (title, content, id)
            )
        db.commit()
        resp = Response()
        resp.headers['HX-Location'] = json.dumps({'path': url_for('argue.premises_details', id=id),
                                                  'target': '#main', 'source': '#htmx-location-source'})
        # no content to send on successful registration
        resp.status_code = 204
        return resp

    item = db.execute(
            "SELECT * FROM premises WHERE id = ?",
            (id,)
            ).fetchone()

    form.title.data = item['title']
    form.content.data = item['content']

    return {'template': 'argue/premises_edit.html', 'context': {'form': form, 'id': id}}

@bp.route('conclusions/<int:id>/edit', methods=('GET', 'PUT'))
@htmx_required
@login_required
def conclusions_edit(id):

    form = ArgumentForm()

    db = get_db()

    if request.method == 'PUT':
        if not form.validate():
            # bad request
            return {'template': 'argue/conclusions_edit.html', 'context':{'form': form}, 'code': 400}

        title = form.title.data
        content = form.content.data

        db.execute(
            "UPDATE conclusion SET title = ?, content = ? WHERE id = ?",
            (title, content, id)
            )
        db.commit()
        resp = Response()
        resp.headers['HX-Location'] = json.dumps({'path': url_for('argue.conclusions_details', id=id),
                                                  'target': '#main', 'source': '#htmx-location-source'})
        # no content to send on successful registration
        resp.status_code = 204
        return resp

    item = db.execute(
            "SELECT * FROM conclusion WHERE id = ?",
            (id,)
            ).fetchone()

    form.title.data = item['title']
    form.content.data = item['content']

    return {'template': 'argue/conclusions_edit.html', 'context': {'form': form, 'id': id}}


@bp.route('/connect', methods=('GET', 'POST'))
@htmx_required
@login_required
def connect():

    db = get_db()
    form = ConnectionForm(request.form)

    if request.method == 'POST':

        if not form.validate():

            # bad request
            return {'template': 'argue/connect.html', 'context':{'form': form}, 'code': 400}

        arg_ids = db.execute("""
                            SELECT id FROM argument WHERE user_id = ?
                            """,
                            (g.user['id'],)
                            ).fetchall()

        try:
            if category == 'premise':
                db.execute("""
                        INSERT INTO argument_premise (argument_id, premise_id) VALUES (?, ?)
                        """,
                        (argument_id, id)
                        )
            elif category == 'conclusion':
                db.execute("""
                        INSERT INTO argument_conclusion (argument_id, conclusion_id) VALUES (?, ?)
                        """,
                        (argument_id, id)
                        )
            db.commit()
        except db.IntegrityError:
            flash("This item is already connected to the argument")
            return htmx_redirect('argue.connect', flash=True)

        return htmx_redirect('argue.overview')


    arguments = db.execute(
            'SELECT * FROM argument WHERE user_id = ? ORDER BY created DESC',
            (g.user['id'],)
            ).fetchall()

    conclusions = db.execute(
            'SELECT * FROM conclusion WHERE user_id = ? ORDER BY created DESC',
            (g.user['id'],)
            ).fetchall()

    premises = db.execute(
            'SELECT * FROM premise WHERE user_id = ? ORDER BY created DESC',
            (g.user['id'],)
            ).fetchall()

    form.argument.choices = [(argument['id'], argument['title']) for argument in arguments]
    form.category.choices = [('premise', 'Premise'), ('conclusion', 'Conclusion')]
    form.connection.choices = [(premise['id'], premise['title']) for premise in premises] 

    return {'template':'argue/connect.html', 'context':{'form':form}}

@bp.route('/share/<int:id>', methods=('GET',))
def share(id):
    db = get_db()

    # get argument info
    argument = db.execute(
            "SELECT * FROM argument WHERE id = ?",
            (id,)
            ).fetchone()

    # get premises and conclusions
    prems = db.execute(
            "SELECT * FROM premise WHERE id IN (SELECT premise_id FROM argument_premise WHERE argument_id = ?)",
            (id,)
            ).fetchall()
    concs = db.execute(
            "SELECT * FROM conclusion WHERE id IN (SELECT conclusion_id FROM argument_conclusion WHERE argument_id = ?)",
            (id,)
            ).fetchall()

    # escape probably not necessary, not using in html, only script tags
    # Build markdown content for premises
    md_prems = '\n'.join([f"- **{prem['title']}**: {prem['content']}\n" for prem in prems])

    # Build markdown content for conclusions
    md_concs = '\n'.join([f"- **{conc['title']}**: {conc['content']}\n" for conc in concs])

    # Construct the entire markdown string
    markdown = (
        f"# Argument Title: {argument['title']}\n\n"
        f"{argument['content']}\n\n"
        "## Premises\n"
        f"{md_prems}\n\n"
        "## Conclusions\n"
        f"{md_concs}\n\n"
        f"---\n\n"
        f"[Link to Full Argument Details]({request.url_root}argue/details/argument/{id})"
    )

    # Escape the markdown for safe inclusion in a JavaScript string
    escaped_markdown = json.dumps(markdown)

    # Generate the script snippet to copy the escaped markdown
    script = f'''
    <script>
        navigator.clipboard.writeText({escaped_markdown})
    </script>
    '''
    return script

@bp.route('/status', methods=('GET',))
def status():
    return render_template('basics/flash.html')
