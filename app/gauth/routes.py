import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from flask_restful import Resource, reqparse
from . import gauth_bp as bp

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request,
    session, url_for, jsonify, make_response
)

from app.db import get_db, exec_sql
import app.dbOps as dbOps
from functools import wraps

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/calendar.settings.readonly',
          'https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.events',
          'https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/drive.metadata.readonly']


class AuthorizationError(Exception):
    def __init__(self):
        self._message = 'Auth Error, re-authenticate user'

    def __str__(self):
        return self._message


@bp.errorhandler(AuthorizationError)
def handle_auth_error(error):
    print(error)
    return flask.redirect(flask.url_for('gauth.authorize'))


# catches internal google errors on acquiring service, raise auth error
def auth_error_on_fail(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            raise AuthorizationError
    return wrapper


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'id' not in flask.session or type(flask.session['id']) != int:
            print('I\'m useful')
            return flask.redirect(flask.url_for('gauth.authorize'))
        return func(*args, **kwargs)
    return wrapper


def no_cache(view):
    @wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return no_cache_impl


@auth_error_on_fail
def gmail_service(credentials):
    return googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)


@auth_error_on_fail
def drive_service(credentials):
    return googleapiclient.discovery.build('drive', 'v2', credentials=credentials)


@auth_error_on_fail
def calendar_service(credentials):
    return googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)


@bp.route('/')
def index():
    return print_index_table()


@bp.route('/test')
@no_cache
@login_required
def test_api_request():
    authorized_user_info = dbOps.Usr.read(flask.session['id'])['token']

    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
        authorized_user_info
    )

    gmail = gmail_service(credentials)

    email = gmail.users().getProfile(userId='me').execute()['emailAddress']
    dbOps.Usr.update(email, credentials)
    return email


@bp.route('/authorize')
@no_cache
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('gauth.oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    flask.session['state'] = state

    return flask.redirect(authorization_url)


@bp.route('/oauth2callback')
@no_cache
def oauth2callback():
    state = flask.session['state']
    flask.session.pop('state')

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)

    flow.redirect_uri = flask.url_for('gauth.oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    gmail = gmail_service(credentials)
    email = gmail.users().getProfile(userId='me').execute()['emailAddress']
    id = dbOps.signin(email, credentials)
    flask.session['id'] = id

    return flask.redirect(flask.url_for('gauth.test_api_request'))


@bp.route('/revoke')
@no_cache
def revoke():
    if 'id' not in flask.session:
        return ('You need to <a href="/auth/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    id = flask.session.pop('id')

    authorized_user_info = dbOps.Usr.read(id)['token']

    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
        authorized_user_info
    )

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())
    else:
        return('An error occurred.' + print_index_table())


@bp.route('/clear')
def clear_credentials():
    if 'id' in flask.session:
        flask.session.pop('id')

    if 'state' in flask.session:
        flask.session.pop('state')

    return ('Credentials have been cleared.<br><br>' +
            print_index_table())


def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/auth/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/auth/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/auth/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/auth/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')

# if __name__ == '__main__':
#     # When running locally, disable OAuthlib's HTTPs verification.
#     # ACTION ITEM for developers:
#     #     When running in production *do not* leave this option enabled.
#     os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#     # Specify a hostname and port that are set as a valid redirect URI
#     # for your API project in the Google API Console.
#     app.run('localhost', 36227, debug=True)
