import urllib2, json

from rauth.service import OAuth2Service
from flask import current_app, url_for, request, redirect, session
from airflow.configuration import conf

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = conf.get('oauth', 'provider')
        self.consumer_id = conf.get('oauth', 'client_id')
        self.consumer_secret = conf.get('oauth', 'client_secret')

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self, scheme='https'):
        return url_for('auth_login.oauth_callback', provider=self.provider_name,
                        _external=True, _scheme=scheme)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers={}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
                name='google',
                client_id=self.consumer_id,
                client_secret=self.consumer_secret,
                authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
                base_url="https://www.googleapis.com/oauth2/v3/userinfo",
                access_token_url="https://www.googleapis.com/oauth2/v4/token"
        )

    def authorize(self, scheme):
        return redirect(self.service.get_authorize_url(
            scope='email profile',
            response_type='code',
            redirect_uri=self.get_callback_url(scheme))
            )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
                data={'code': request.args['code'],
                      'grant_type': 'authorization_code',
                      'redirect_uri': self.get_callback_url()
                     },
                decoder = json.loads
        )
        me = oauth_session.get('').json()
        return (me['name'],
                me['sub'],
                me['email'])

