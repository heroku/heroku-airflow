from flask import Blueprint, redirect, url_for, request, current_app
from airflow.plugins_manager import AirflowPlugin


YEAR_IN_SECS = 31536000
ssl_bp = Blueprint('ssl_everything', __name__)

@ssl_bp.before_app_request
def before_request():
    app = current_app._get_current_object()
    criteria = [
        request.is_secure,
        app.debug,
        request.headers.get('X-Forwarded-Proto', 'http') == 'https'
    ]

    if not any(criteria):
        if request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            r = redirect(url, code=302)
            return r

@ssl_bp.after_app_request
def after_request(response):
    hsts_policy = 'max-age={0}'.format(YEAR_IN_SECS)
    response.headers.setdefault('Strict-Transport-Security', hsts_policy)
    return response

class AirflowSSLPlugin(AirflowPlugin):
    name = 'ssl_everything'
    flask_blueprints = [ssl_bp]
