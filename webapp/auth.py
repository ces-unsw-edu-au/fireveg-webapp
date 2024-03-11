import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError  # Add this import for IntegrityError
from webapp.db import get_db
from webapp.emails.Users.SignupEmailVerification import SignupEmailVerification
from webapp.emails.Users.ForgotPasswordEmail import ForgotPasswordEmail
from webapp.helpers.String.StringHelpers import generate_random_string_using_time, add_days_to_current_date_time, add_seconds_to_current_date_time
bp = Blueprint('auth', __name__, url_prefix='/auth')

from webapp.models.Users import Users
from webapp.models.RoleUpgradeRequests import RoleUpgradeRequests

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
                flash('Please check your email for email verification.')
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


@bp.route('/forgot_password', methods=('GET', 'POST'))
def forgot_password():
    print("auth.forgot_password")
    if request.method == 'POST':
        username = request.form['username']
        print("username in forgot_password")
        print("username in forgot_password")
        print(username)
        db = get_db()
        error = None
        user = Users.query.filter_by(username=username).first()
        if user is None:
            error = 'Incorrect username.'
        if(error):
            flash(error)
            return redirect(url_for('auth.forgot_password'))
        
        db = get_db()
        objUser = Users.query.get(user.id)
        objUser.password_reset_token = generate_random_string_using_time()
        objUser.password_reset_token_expiry_time = add_days_to_current_date_time(7)
        db.session.commit()
        subject = "Your Password Reset Information on fireveg"
        ForgotPasswordEmail.send_forgot_password_email_letter(objUser.username,subject,objUser)
        flash('Forgot Password Email Sent, Successfully! Please check your email.') 
        # return redirect(url_for('auth.forgot_password'))
        return render_template('auth/forgot_password.html')
    else: 
        # return redirect(url_for('auth.forgot_password'))
        return render_template('auth/forgot_password.html')


@bp.route('/password_reset', methods=('GET', 'POST'))
def password_reset():
    id = request.args.get('id', type=int)
    password_reset_token = request.args.get('password_reset_token')
    print("id in password_reset")
    print("id in password_reset")
    print(id)
    print("password_reset_token in password_reset")
    print("password_reset_token in password_reset")
    print(password_reset_token)
    if id is None or password_reset_token is None:
        flash('Invalid url.')
        return redirect(url_for('auth.login'))
    # objUser = Users.query.filter_by(email=email).first()
    objUser = Users.query.get(id)
    print("objUser in password_reset")
    print("objUser in password_reset")
    print(objUser)
    if not objUser:
        flash('Invalid url.')
        return redirect(url_for('auth.login'))
    if objUser.password_reset_token != password_reset_token:
        flash('Invalid url forgot password reset url.')
        return redirect(url_for('auth.login'))
    now = datetime.utcnow()
    password_reset_token_expiry_time = objUser.password_reset_token_expiry_time
    print(now)
    print("now")
    print(password_reset_token_expiry_time)
    print("password_reset_token_expiry_time")
    if now > password_reset_token_expiry_time:
        flash('Your link has been expired. Please go to the forgot password form and fill out the form again!')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if(password != confirm_password):
            flash('Password and confirm password do not match.')
            return redirect(url_for('auth.password_reset', id=id, password_reset_token=password_reset_token))
        db = get_db()
        user = Users.query.get(objUser.id)
        user.password = generate_password_hash(password)
        user.password_reset_token = None
        db.session.commit()
        flash('Password changed successfully, You can now log in.')
        return redirect(url_for('auth.login'))
        # return render_template('auth/login.html')
    else: 
        # return redirect(url_for('auth.forgot_password'))
        return render_template('auth/password_reset_from_email.html')

    # db = get_db()
    # user = Users.query.get(objUser.id)
    # user.password = generate_password_hash(password)
    # user.password_reset_token = None
    # db.session.commit()
    # flash('Password changed successfully, You can now log in.')
    # return redirect(url_for('auth.password_reset_from_email'))
    # return render_template('auth/password_reset_from_email.html')


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

@bp.route('/change_password', methods=('GET', 'POST'))
@login_required
def change_password():
    
    print("g.user in change_password")
    print("g.user in change_password")
    print(g.user)
    print("g.user.id in change_password")
    print("g.user.id in change_password")
    print(g.user.id)
    id = g.user.id
    objUser = Users.query.get(id)
    print("objUser in change_password")
    print("objUser in change_password")
    print(objUser)
    if not objUser:
        flash('Invalid url.')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        old_password = request.form['old_password']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if not check_password_hash(objUser.password, old_password):
            flash('Password do not match with old password.')
            return redirect(url_for('auth.change_password'))
        if(password != confirm_password):
            flash('Password and confirm password do not match.')
            return redirect(url_for('auth.change_password'))
        db = get_db()
        user = Users.query.get(objUser.id)
        user.password = generate_password_hash(password)
        db.session.commit()
        flash('Password changed successfully')
        return redirect(url_for('auth.change_password'))
        # return render_template('auth/login.html')
    else: 
        return render_template('auth/change_password.html')
    

@bp.route('/upgrade_request', methods=('GET', 'POST'))
@login_required
def upgrade_request():
    
    print("g.user in upgrade_request")
    print("g.user in upgrade_request")
    print(g.user)
    print("g.user.id in upgrade_request")
    print("g.user.id in upgrade_request")
    print(g.user.id)
    id = g.user.id
    objUser = Users.query.get(id)
    print("objUser in upgrade_request")
    print("objUser in upgrade_request")
    print(objUser)
    if not objUser:
        flash('Invalid url.')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        existing_request = RoleUpgradeRequests.query.filter_by(user_id=g.user.id).first()

        if existing_request:
            flash('You have already submitted a role upgrade request.', 'info')
            return redirect(url_for('dataexport.download_file'))
        else:
            # Add a new record to RoleUpgradeRequests for the logged-in user
            db = get_db()
            upgrade_request = RoleUpgradeRequests(role_name='downloader', user_id=g.user.id)
            db.session.add(upgrade_request)
            db.session.commit()
            
            flash('Role upgrade request submitted successfully!')
            return redirect(url_for('dataexport.download_file'))
        # return render_template('auth/login.html')
    else: 
        return redirect(url_for('dataexport.download_file'))
        # return render_template('auth/upgrade_request.html')