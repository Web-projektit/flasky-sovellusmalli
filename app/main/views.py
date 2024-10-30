from flask import render_template,request,flash,redirect,url_for,jsonify,current_app
from flask_login import login_required
from ..decorators import admin_required
from ..models import User
from app import db
from . import main


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/edit_profile_admin', methods=['GET', 'POST']) 
@login_required
@admin_required
def edit_profile_admin():
    return "rakenteilla"
    
 

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
            db.session.execute(query)
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
