from datetime import datetime
from flask import current_app
import flask_login
from flask_login import login_required, current_user, logout_user

from sqlalchemy import (Column, DateTime, String, Boolean)

from airflow import settings
from airflow import models


DEFAULT_USERNAME = 'airflow'

login_manager = flask_login.LoginManager()
login_manager.login_view = 'airflow.login'  # Calls login() bellow
login_manager.login_message = None


class User(models.BaseUser):
    provider_id = Column('provider_id', String(300))
    registered_on = Column('registered_on' , DateTime)

    def __init__(self, username, email, provider_id):
        self.username = username
        self.email = email
        self.provider_id = provider_id
        self.registered_on = datetime.utcnow()

    def is_active(self):
        '''Required by flask_login'''
        return True

    def is_authenticated(self):
        '''Required by flask_login'''
        return True

    def is_anonymous(self):
        '''Required by flask_login'''
        return False

    def data_profiling(self):
        '''Provides access to data profiling tools'''
        return True

    def is_superuser(self):
        '''Access all the things'''
        return True

models.User = User  # hack!
del User

# Have to do it here because of user model imports
from airflow_auth import OAuthSignIn


@login_manager.user_loader
def load_user(userid):
    session = settings.Session()
    if userid == "None":
        userid = None
    to_return = session.query(models.User).filter(models.User.id == userid).first()
    session.expunge_all()
    session.commit()
    session.close()
    return to_return

def login(self, request):
    if not current_user.is_anonymous:
        return None
    app = current_app._get_current_object()
    criteria = [
        request.is_secure,
        app.debug == False,
        request.headers.get('X-Forwarded-Proto', 'http') == 'https'
    ]
    scheme = 'http'
    if any(criteria):
        scheme = 'https'
    oauth = OAuthSignIn.get_provider('google')
    return oauth.authorize(scheme)
