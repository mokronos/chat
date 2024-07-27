from flask import render_template, url_for
from flask import Response
import functools
import json
from ..htmx import htmx


def htmx_required(view):

    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):

        if htmx:
            base_template = 'basics/_partial.html'
        else:
            base_template = 'base.html'


        return_obj= view(*args, **kwargs)

        # if the view redirects, return the redirect instead of rendering
        # if type(return_obj) == Response and 300 <= return_obj._status_code <= 399:
        #     return return_obj
        # this is probably fine as well
        if type(return_obj) == Response:
            return return_obj
        elif type(return_obj) == str:
            print("returning string")
            return render_template(return_obj, base_template=base_template)

        template = ""
        context = {}
        headers = {}
        code = 200
        if type(return_obj) == dict:
            template = return_obj.get('template')
            context = return_obj.get('context', {})
            headers = return_obj.get('headers', {})
            code = return_obj.get('code', 200)

        content = render_template(template, **context, base_template=base_template)
        resp = Response(content)
        resp.status_code = code
        for key, value in headers.items():
            resp.headers[key] = value
        return resp

    return wrapped_view

def htmx_redirect(view, code=204, target="#main", source="#htmx-location-source", flash=False):
    resp = Response()
    resp.status_code = code
    resp.headers['HX-Location'] = json.dumps({'path': url_for(view), 'target': target, 'source': source})
    if flash:
        resp.headers['HX-Trigger'] = 'status-changed'
    print(resp.headers)
    return resp
    
