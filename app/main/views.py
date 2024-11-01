from flask import render_template,request,flash,redirect,url_for,jsonify,current_app,send_from_directory
from flask_login import login_required,current_user
from ..decorators import admin_required
from ..models import User
from .forms import ProfileForm
from app import db
from . import main
from sqlalchemy import text
import os
from werkzeug.utils import secure_filename


def shorten(filename):
    name, extension = os.path.splitext(filename)
    print("SHORTEN:"+name+" "+extension)
    length = 64 - len(extension)
    return name[:length] + extension

def allowed_file(filename):
    app = current_app._get_current_object()
    ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def tee_kuvanimi(id,kuva):
    return str(id) + '_' + kuva

def poista_vanha_kuva(id,kuva):
    kuvanimi = tee_kuvanimi(id,kuva)
    app = current_app._get_current_object()
    KUVAPOLKU = app.config['KUVAPOLKU']
    filename = os.path.join(KUVAPOLKU, kuvanimi)
    print("POISTETAAN:"+filename)
    try:
        os.remove(filename)
    except Exception as e:
        app.logger.info(e)
        return False
    else:   
        return True

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/img/')
@main.route('/img/<path:filename>')
def img(filename = None):
    app = current_app._get_current_object()
    KUVAPOLKU = app.config['KUVAPOLKU']
    if filename is None:
        filename = 'default_profile.png'
    return send_from_directory(KUVAPOLKU, filename)

@main.route('/edit_profile', methods=['GET', 'POST'])  
@login_required
def edit_profile():
    user = User.query.get_or_404(current_user.id)
    form = ProfileForm(obj=user)
    app = current_app._get_current_object()
    KUVAPOLKU = app.config['KUVAPOLKU']
    if form.validate_on_submit():
        # check if the post request has the file part
        if 'img' in request.files:
            file = request.files['img']
            kuvanimi = file.filename
            if current_user.img and kuvanimi != current_user.img:
                poista_vanha_kuva(current_user.id,current_user.img)
            if kuvanimi and allowed_file(kuvanimi):
                # Lomakkeelta lähetettynä paikallinen tallennus,
                # S3- ja Azure-tallennus tehty erikseen Javascriptillä
                kuvanimi = shorten(secure_filename(kuvanimi))
                filename = tee_kuvanimi(current_user.id,kuvanimi)
                file.save(os.path.join(KUVAPOLKU, filename))
        form.populate_obj(user)
        user.img = kuvanimi
        # db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    if user.img:
        kuva = tee_kuvanimi(user.id,user.img) 
        # kuva = os.path.join(KUVAPOLKU, kuva)
    else:
        kuva = ''    
    return render_template('edit_profile.html', form=form,kuva=kuva)



    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('.user', username=current_user.username))
    return render_template('edit_profile.html', form=form)

@main.route('/edit_profile_admin', methods=['GET', 'POST']) 
@login_required
@admin_required
def edit_profile_admin():
    return "rakenteilla"
    
@main.route('/user', methods=['GET'])
@login_required
def user(): 
    return render_template('user.html',user=current_user,kuva=False)   

@main.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    if request.form.get('painike'):
        users = request.form.getlist('users')
        if len(users) > 0:
            query_start = "INSERT INTO users (id,active) VALUES "
            query_end = " ON DUPLICATE KEY UPDATE active = VALUES(active)"
            query_values = ""
            active = request.form.getlist('active')
            for v in users:
                if v in active:
                    query_values += "("+v+",1),"
                else:
                    query_values += "("+v+",0),"
                # query_values += "("+v+"," + ("1" if v in active else "0") + "),"        
                # query_values += f"({v}, {'1' if v in active else '0'}),"
            query_values = query_values[:-1]
            query = query_start + query_values + query_end
            # print("\n"+query+"\n")
            # result = db.session.execute('SELECT * FROM my_table WHERE my_column = :val', {'val': 5})
            db.session.execute(text(query))
            db.session.commit()
            # return query
            #return str(request.form.getlist('users')) + \
            #       "<br>" + \
            #        str(request.form.getlist('active'))
        else:
            flash("Käyttäjälista puuttuu.")
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.name).paginate(
        page=page, per_page=current_app.config.get('FS_POSTS_PER_PAGE', 25),
        error_out=False)
    lista = pagination.items
    return render_template('users.html',users=lista,pagination=pagination,page=page)

@main.route('/poista', methods=['GET', 'POST'])
@login_required
@admin_required
def poista():
    # print("POISTA:"+request.form.get('id'))
    user = User.query.get(request.form.get('id'))
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        flash(f"Käyttäjä {user.name} on poistettu")
        return jsonify(OK="käyttäjä on poistettu.")
    else:
        return jsonify(virhe="käyttäjää ei löydy.")





    return render_template('users.html')
