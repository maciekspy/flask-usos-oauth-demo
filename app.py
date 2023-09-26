from os import environ
import requests
from dotenv import load_dotenv

from flask import Flask, redirect, url_for, render_template, flash, session, current_app, request, abort
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from authlib.integrations.flask_client import OAuth
from authlib.common.urls import add_params_to_uri
from models import db, User

# Load and check environment variables
load_dotenv()
assert 'APP_SECRET_KEY' in environ, "Set APP_SECRET_KEY environment variable"
assert 'SQLALCHEMY_DATABASE_URI' in environ, "Set SQLALCHEMY_DATABASE_URI environment variable"
assert 'USOS_CUSTOMER_KEY' in environ and 'USOS_CUSTOMER_SECRET' in environ, \
    "Set USOS_CUSTOMER_KEY and USOS_CUSTOMER_SECRET environment variable" \
    "You can get them at: https://apps.usos.pw.edu.pl/developers/"

app = Flask(__name__)
app.config['SECRET_KEY'] = environ.get('APP_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

oauth = OAuth(app)
usos_pw = oauth.register('usos_pw',
    api_base_url='https://apps.usos.pw.edu.pl/',
    request_token_url='https://apps.usos.pw.edu.pl/services/oauth/request_token',
    # List of available request token scopes: 
    # https://apps.usos.pw.edu.pl/developers/api/authorization/#scopes
    request_token_params={ 'data': {'scopes': '|'.join(['email', 'studies'])}},
    access_token_url='https://apps.usos.pw.edu.pl/services/oauth/access_token',
    access_token_params=None,
    authorize_url='https://apps.usos.pw.edu.pl/services/oauth/authorize',
    authorize_params=None,
    
    client_id=environ.get('USOS_CUSTOMER_KEY'),
    client_secret=environ.get('USOS_CUSTOMER_SECRET'),
    client_kwargs=None,
)

db.init_app(app)
login = LoginManager(app)
login.login_view = 'index'

@login.user_loader
def load_user(user_id):
    if user_id == 'None':
        return None
    return db.session.query(User).filter_by(id = int(user_id)).one_or_none()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('usos_pw_token', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/authorize')
def oauth_authorize():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    callback_url = url_for('oauth_authorized', _external=True,
                           next=request.args.get('next') or request.referrer or None)

    return oauth.usos_pw.authorize_redirect(callback_url)

def request_user_data(user_fields):
    uri = add_params_to_uri('https://apps.usos.pw.edu.pl/services/users/user', [('fields', '|'.join(user_fields))] )
    response = oauth.usos_pw.get(uri)
    
    if response.ok:
        return response.json()
    
    return None

@app.route('/oauth-authorized')
def oauth_authorized():
    
    token = oauth.usos_pw.authorize_access_token()
    
    next_url = request.args.get('next') or url_for('index')
    if token is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    # Save user token data in session
    session['usos_pw_token'] = (
        token['oauth_token'],
        token['oauth_token_secret']
    )
    
    # Get user data
    # https://apps.usos.pw.edu.pl/developers/api/services/users/#user
    user_fields = ['id', 'first_name', 'last_name', 'email', 'student_number', 'student_programmes'] 
    user_data = request_user_data(user_fields)

    if user_data is None:
        flash("Could not get user data!", "error")
        return redirect(next_url)
    
    app.logger.info('user_data: %s', user_data)

    usos_id = int(user_data['id'])
    first_name = user_data['first_name']
    last_name = user_data['last_name']
    email = user_data['email']
    student_number  = user_data['student_number']

    flash(f'You were signed in as {first_name} {last_name}')
    
    # find or create the user in the database
    user = db.session.query(User).filter(User.usos_id==usos_id).one_or_none()
    if user is None:
        user = User(usos_id=usos_id, student_number=student_number,
                    first_name=first_name, last_name=last_name,
                    email=email)
        db.session.add(user)
        db.session.commit()
    else: 
        # check if user data are up to date
        if user.first_name != first_name:
            app.logger.info('First name of user (%d) has changed from "%s" to "%s"', user.id, user.first_name, first_name)
            user.first_name = first_name
            db.session.commit()
        if user.last_name != last_name:
            app.logger.info('Last name of user (%d) has changed from "%s" to "%s"', user.id, user.last_name, last_name)
            user.last_name = last_name
            db.session.commit()
        if user.student_number != student_number:
            app.logger.info('Student number of user (%d) has changed from "%s" to "%s"', user.id, user.student_number, student_number)
            user.student_number = student_number
            db.session.commit()
        if user.email != email:
            app.logger.info('Email of user (%d) has changed from "%s" to "%s"', user.id, user.email, email)
            user.email = email
            db.session.commit()

    # log the user in
    login_user(user)
    
    return redirect(next_url)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)