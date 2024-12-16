from flask import render_template,request, \
     flash,redirect,url_for,jsonify,current_app, \
     send_from_directory, make_response
from flask_login import (
    login_user,logout_user, 
    login_required, current_user )
from ..decorators import admin_required,debuggeri
from ..models import User
from ..auth.forms import LoginForm, SignupForm
from ..email import send_email
from app import db
from . import reactapi
from sqlalchemy import text
import os
import sys
from werkzeug.utils import secure_filename
from flask_babel import _
import json
from flask_wtf.csrf import generate_csrf,CSRFError
import time

def createResponse(message, status_code=200):
    # CORS:n vaatimat Headerit
    default_origin = 'http://localhost:5176'
    default_origin = current_app.config.get('DEFAULT_ORIGIN',default_origin)
    origin = request.headers.get('Origin',default_origin)
    response = make_response(jsonify(message))
    # Access-Control-Allow-Credentials
    # response.headers.set('Access-Control-Allow-Credentials',True)
    response.headers.set('Access-Control-Allow-Origin',origin)
    response.status_code = status_code
    return response


@reactapi.app_errorhandler(401)
def page_not_allowed(e):
    app = current_app._get_current_object()
    app.logger.debug('reactapi.app_errorhandler 401,endpoint %s', request.endpoint)
    app.logger.debug('reactapi.app_errorhandler 401,path %s', request.path)
    if request.endpoint == 'reactapi.confirm':
        # Vrt. vastaava Flask route:
        # login_url = url_for('login', confirm_token=confirm_token, _external=True)
        redirect_url = app.config['REACT_LOGIN'] + "?next=" + request.path
        return redirect(redirect_url)
    message = {'virhe':'Kirjautuminen puuttuu.'}
    return createResponse(message)


@reactapi.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    message = {'virhe':f'csrf-token puuttuu ({e.description}), headers:{str(request.headers)}'}
    sys.stderr.write(f"\nreactapi CSFRError,headers:{str(request.headers)}\n")
    return createResponse(message, status_code=400)


@reactapi.route('/getcsrf', methods=['GET'])
def getcsrf():
    token = generate_csrf()
    response = jsonify({"detail": "CSRF cookie set"})
    response.headers.set("X-CSRFToken", token)
    return response

@reactapi.route('/signin', methods=['GET','POST'])
def signin():
    print("reactapi,views.py,LOGIN")
    form = LoginForm()
    sys.stderr.write(f"\nreactapi,views.py,LOGIN data:{form.email.data}\n")
    if form.validate_on_submit():
        sys.stderr.write(f"\nreactapi, views.py,LOGIN, validate_on_submit OK\n")
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            sys.stderr.write(f"\nviews.py,LOGIN, request.args:{request.args}\n")
            next = request.args.get('next')
            sys.stderr.write(f"\nviews.py,LOGIN:OK, next:{next}, confirmed:{user.confirmed}\n")
            if next is None or not next.startswith('/'):
                if user.confirmed:
                    response = jsonify({'success':True,'confirmed':'1'})
                    response.status_code=200
                    return response
                else:
                    response = jsonify({'success':True})
                    response.status_code=200
                    return response
            return redirect(next)
        else:
            response = jsonify({'success':False,'message':"Väärät tunnukset"})
            response.status_code = 401
            return response
    else:
        response = jsonify({
            "success": False,
            "message": "Tiedot on annettu väärin.",
            "errors": form.errors })
        response.status_code=400
        return response
    

@reactapi.route('/signup', methods=['GET', 'POST'])
# Määritetään CORS-alustuksessa
# @cross_origin(supports_credentials=True)
def signup():
    form = SignupForm()
    sys.stderr.write('\nviews.py,SIGNUP,email:'+form.email.data+'\n')
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'reactapi/email/confirm', user=user, token=token)
        # Huom. ilmoitus sähköpostivahvistuksesta tarvitaan käyttöliittymään
        # flash('A confirmation email has been sent to you by email.')
        response = jsonify({'success':True,'data':'OK'})
        response.status_code = 200
        return response
    else:
        sys.stderr.write("validointivirheet:"+str(form.errors))
        # return "Virhe lomakkeessa:"+str(form.errors)
        response = jsonify({'success':False,
                           'message':'Tiedot väärin.',
                           'errors':form.errors})
        response.status_code = 200
        return response


@reactapi.route('/logout', methods=['GET'])
def logout():
    logout_user()
    response = jsonify({'success':True})
    response.status_code=200
    return response


@reactapi.route('/confirm/<token>', methods=['GET'])
@login_required
def confirm(token):
    if current_user.confirmed:
        response = jsonify({'success':True,
                            'message':'Tunnus on jo vahvistettu',
                            'redirect':'/confirmed'})
        response.status_code = 200
        return response
    if current_user.confirm(token):
        db.session.commit()
        response = jsonify({'success':True,
                            'message':'Tunnus on vahvistettu',
                            'confirmed':'1'
                            })
        response.status_code = 200
        return response
    else:
        response = jsonify({'success':False,
                            'message':'Vahvistus epäonnistui'})
        response.status_code = 200
        return response