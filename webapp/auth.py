import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError  # Add this import for IntegrityError
from webapp.db import get_db
from webapp.emails.Users.SignupEmailVerification import SignupEmailVerification
from webapp.helpers.String.StringHelpers import generate_random_string_using_time
bp = Blueprint('auth', __name__, url_prefix='/auth')

from webapp.models.Users import Users
# print(Users)
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        # print("username")
        # print("username")
        # print("username")
        # print("username")
        # print("username")
        # print("username")
        # print(username)
        if error is None:
            try:
                email_verification_code = generate_random_string_using_time()
                print("email_verification_code")
                print("email_verification_code")
                print("email_verification_code")
                print(email_verification_code)
                new_user = Users(
                    username=username, email=username, password=generate_password_hash(password),
                    email_verification_code=email_verification_code,
                )
                db.session.add(new_user)
                db.session.commit()
                last_inserted_user_id = new_user.id
                print("new_user")
                print("new_user")
                print("new_user")
                print(new_user)
                print("new_user.id")
                print("new_user.id")
                print("new_user.id")
                print(new_user.id)
                print("new_user.email")
                print("new_user.email")
                print("new_user.email")
                print(new_user.email)
                subject = "Please verify your email address"
                SignupEmailVerification.send_signup_verify_email_letter(username,subject,new_user)
                # db.execute(
                #     "INSERT INTO user (username, password) VALUES (?, ?)",
                #     (username, generate_password_hash(password)),
                # )
                # db.commit()
            except IntegrityError:
            # except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("username")
        print("username")
        print(username)
        db = get_db()
        error = None
        # user = db.execute(
        #     'SELECT * FROM user WHERE username = ?', (username,)
        # ).fetchone()
        user = Users.query.filter_by(username=username).first()
        # print("user")
        # print("user")
        # print(user)
        # print("password")
        # print("password")
        # print(password)
        # print("user.id")
        # print("user.id")
        # print(user.id)
        # print("user.email")
        # print("user.email")
        # print(user.email)
        # print("user.password")
        # print("user.password")
        # print(user.password)
        # print("user['password']")
        # print("user['password']")
        # print(user['password'])
        if user is None:
            error = 'Incorrect username.'
        else:
            if not check_password_hash(user.password, password):
            # if not check_password_hash(user['password'], password):
                error = 'Incorrect password.'
        # elif not check_password_hash(user['password'], password):
        #     error = 'Incorrect password.'
        if error is None:
            if user.is_email_verified == False:
                flash('Email is not verified.')
                # _redirect_url = url_for('auth.resend_verify_email')
                # # print("_redirect_url")
                # # print("_redirect_url")
                # # print(_redirect_url)
                # redirect_url = f"{_redirect_url}?is_show_verify_email_button=yes"
                # # print("redirect_url")
                # # print("redirect_url")
                # # print(redirect_url)
                # return redirect(redirect_url)
                return redirect(url_for('auth.resend_verify_email'))
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/verify_email', methods=('GET', 'POST'))
def verify_email():
    id = request.args.get('id', type=int)
    verification_code = request.args.get('verification_code')
    print("id in verify_email")
    print("id in verify_email")
    print(id)
    print("verification_code in verify_email")
    print("verification_code in verify_email")
    print(verification_code)
    if id is None or verification_code is None:
        flash('Invalid url.')
        return redirect(url_for('auth.login'))
    # objUser = Users.query.filter_by(email=email).first()
    objUser = Users.query.get(id)
    print("objUser in verify_email")
    print("objUser in verify_email")
    print(objUser)
    if not objUser:
        flash('Invalid url.')
        return redirect(url_for('auth.login'))
    if objUser.is_email_verified:
        flash('Email already verified.')
        return redirect(url_for('auth.login'))
    if objUser.email_verification_code != verification_code:
        flash('Invalid url email verification.')
        return redirect(url_for('auth.login'))
    db = get_db()
    user = Users.query.get(objUser.id)
    user.is_email_verified = True
    user.email_verification_code = None
    db.session.commit()
    flash('Email verification successful! You can now log in.')
    return redirect(url_for('auth.login'))
    # return render_template('auth/login.html')


@bp.route('/resend_verify_email', methods=('GET', 'POST'))
def resend_verify_email():
    print("auth.resend_verify_email")
    if request.method == 'POST':
        username = request.form['username']
        print("username in resend_verify_email")
        print("username in resend_verify_email")
        print(username)
        db = get_db()
        error = None
        user = Users.query.filter_by(username=username).first()
        if user is None:
            error = 'Incorrect username.'
        if error is None:
            if user.is_email_verified:
                flash('Email is already verified, Please login')
                return redirect(url_for('auth.login'))
        else:
            flash(error)
            return redirect(url_for('auth.resend_verify_email'))


        
        
        db = get_db()
        objUser = Users.query.get(user.id)
        objUser.email_verification_code = generate_random_string_using_time()
        db.session.commit()
        subject = "Please verify your email address"
        SignupEmailVerification.send_signup_verify_email_letter(objUser.username,subject,objUser)
        flash('Resend email verification successful! Please check your email.') 
        # return redirect(url_for('auth.resend_verify_email'))
        return render_template('auth/resend_verify_email.html')
    else: 
        # return redirect(url_for('auth.resend_verify_email'))
        return render_template('auth/resend_verify_email.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # g.user = get_db().execute(
        #     'SELECT * FROM user WHERE id = ?', (user_id,)
        # ).fetchone()
        g.user = Users.query.get(user_id)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
