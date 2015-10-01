import flask_login
from flask_login import login_required, current_user, logout_user
from airflow_auth import OAuthSignIn
from airflow.plugins_manager import AirflowPlugin
from airflow import settings
from airflow import models
from flask import Blueprint, url_for, redirect


auth_login = Blueprint('auth_login', __name__)

# This needs to go into an Airflow Plugin
# see the documentation here: http://pythonhosted.org/airflow/plugins.html
@auth_login.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    username, uid, email = oauth.callback()
    if uid is None:
        print "failed auth"
        flash('Authentication failed.')
        return redirect(url_for('index'))

    session = settings.Session()
    user = session.query(models.User).filter(
        models.User.provider_id == uid).first()
    if not user:
        user = models.User(
                username=username,
                provider_id=uid,
                email=email)
        session.add(user)
        session.flush()
        session.commit()
    flask_login.login_user(user)
    session.close()
    return redirect(url_for('index'))

class AirflowOauthPlugin(AirflowPlugin):
    name = 'oauth_plugin'
    flask_blueprints = [auth_login]
