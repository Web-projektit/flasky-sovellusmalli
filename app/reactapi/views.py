from flask import render_template,request, \
     flash,redirect,url_for,jsonify,current_app, \
     send_from_directory, make_response
from flask_login import (
    login_user,logout_user, 
    login_required, current_user )
from ..decorators import admin_required,debuggeri
from ..models import User
from ..auth.forms import LoginForm
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
            "message": "iedot on annettu väärin.",
            "errors": form.errors })
        response.status_code=400
        return response
