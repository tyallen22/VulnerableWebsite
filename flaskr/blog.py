from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.auth import session
from wtforms import Form, StringField, SelectField
from .forms import DateSearchForm

bp = Blueprint('blog', __name__)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    secret = 'dev'
    if request.method == 'POST':

        key = request.form['token']

        if key == 'dev':
            results = []
            total = request.form['amount']
            account = request.form['account']
            db = get_db()
            cursor = db.cursor()
            name = session.get('username')
            print(name)
            error = None

            if total is None:
                error = 'Transfer amount is required.'

            if account is None:
                error = 'Account username is required'

            if error is not None:
                flash(error)
            else:
                cursor.execute("SELECT balance FROM accounts WHERE username = %s", [name])
                current_balance_user = cursor.fetchone()
                cursor.execute("SELECT balance FROM accounts WHERE username = %s", [account])
                current_balance_target = cursor.fetchone()

                if current_balance_target is not None:
                    if int(total) <= int(current_balance_user[0]):

                        new_balance_user = int(current_balance_user[0]) - int(total)
                        new_balance_target = int(current_balance_target[0]) + int(total)
                        cursor.execute("UPDATE accounts SET balance = %s WHERE username = %s", (new_balance_target, account))
                        cursor.execute("UPDATE accounts SET balance = %s WHERE username = %s", (new_balance_user, name))
                        db.commit();

                        cursor.execute("SELECT * FROM accounts WHERE username = %s OR username = %s", (name, account))
                        if cursor.rowcount > 0:
                            results = cursor.fetchall()

                        return render_template('blog/create.html', results=results)

    return render_template('blog/create.html')


@bp.route('/update', methods=('GET', 'POST'))
def update():
    search = DateSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('blog/update.html', form=search)

def search_results(search):
    results = []
    user_id = session.get('user_id')
    search_string = search.data['search']
    db = get_db()
    cursor = db.cursor()
    name = session.get('username')
    print(name)
    query = "SELECT * FROM transactions WHERE date = '" + search_string + "' AND username = '" + name + "'"
    print(query)
    cursor.execute(query)
    if cursor.rowcount > 0:
        results = cursor.fetchall()

    return render_template('blog/update.html', form=search, results=results)

@bp.route('/index', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        key = request.form['secretWord']
        user_id = session.get('user_id')
        db = get_db()
        cursor = db.cursor()
        error = None

        if not key:
            error = 'Secret Word is required.'

        if error is not None:
            flash(error)

        if error is None:
            cursor.execute(
                "UPDATE users SET secretKey = %s WHERE username LIKE %s",
                (key, g.user[1])
            )

            db.commit()
            return redirect(url_for('blog.index'), user_id=user_id, key=key)

    elif request.method == 'GET':
        usr_id = request.args.get('user_id')
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT username FROM stalim WHERE CAST(id as CHAR) LIKE %s", [usr_id]
        )

        res = make_response(render_template('blog/index.html'))
        if g.user is not None:
            res.set_cookie('username', g.user[1], max_age=5)
            res.set_cookie('password', g.user[2], max_age=5)

        return res
