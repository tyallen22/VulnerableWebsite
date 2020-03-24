import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        cursor.execute(
            "SELECT username FROM users WHERE username LIKE %s", [username]
        )
        user = cursor.fetchone()

        if user is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (%s, %s)',
                (username, password)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None

        cursor.execute(
            "SELECT username FROM users WHERE username LIKE %s", [username]
        )
        user = cursor.fetchone()
        cursor.execute(
            "SELECT password FROM users WHERE username LIKE %s", [username]
        )
        pw = cursor.fetchone()

        if user is None:
            error = 'Incorrect username.'
        # elif not check_password_hash(user['password'], password):
            # error = 'Incorrect password.'

        elif not (pw[0] == password):
            error = 'Incorrect password.'

        if error is None:
            print("user: " + user[0] + " and password: " + pw[0]);
            cursor.execute(
                "SELECT id FROM users WHERE username LIKE %s", [username]
            )
            userid = cursor.fetchone()
            user_id = str(userid[0])
            session['user_id'] = user_id

            # session['user_id'] = user['id']
            return redirect(url_for('blog.index', user_id=user_id))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = request.args.get('user_id')
    db = get_db()
    cursor = db.cursor()

    if user_id is None:
        g.user = None
    else:
        # userid = str(user_id[0])
        # print("user id is " + userid)
        cursor.execute(
            "SELECT * FROM users WHERE CAST(id as CHAR) LIKE %s", [user_id]
        )
        g.user = cursor.fetchone()

        # print("user logged in is " + str(g.user[1]))
        # return res


@bp.route('/hello', methods=('GET', 'POST'))
def hello():
    if request.method == 'POST':
        username = username

        return render_template('auth/helloWorld.html',username=username)

        flash(error)

    return render_template('auth/helloWorld.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
