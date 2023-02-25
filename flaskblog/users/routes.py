from flask import render_template, url_for, flash, redirect, request, jsonify
from flaskblog import db, bcrypt
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateForm, RequestResetForm, ResetPasswordForm
from flaskblog.models import User, Votes
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint
from flaskblog.users.utils import save_picture, get_likes, get_dislikes, send_reset_email

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register_me():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('./auth/register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('./auth/login.html', title='Login', form=form)


@users.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateForm()
    image_file = './static/profile_images/default.jpg'
    if form.validate_on_submit():
        if not form.username.data and not form.email.data and not form.picture.data:
            flash('At least one field should be filled!', 'danger')
            return redirect(url_for('profile'))
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_images/' + current_user.image_file)
    return render_template('profile.html', title='Profile', form=form, image_file=image_file)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/vote/like', methods=['GET', 'POST'])
@login_required
def vote_like():
    if request.method == 'POST':
        post_id = request.form.get("post_id")  
        status = Votes.query.filter_by(post_id=post_id, user_id=current_user.id).first()
        if status:
            if status.like == 1:
                status.like = 0
            elif status.like == 0:
                status.like = 1
                status.dislike = 0    
        if not status:
            like = Votes(post_id=post_id, user_id=current_user.id, like=1, dislike=0)
            db.session.add(like)
        db.session.commit()
        likes = get_likes()
        dislikes = get_dislikes()
    return jsonify({'likes': likes, 'dislikes': dislikes})


@users.route('/vote/dislike', methods=['GET', 'POST'])
@login_required
def vote_dislike():
    if request.method == 'POST':
        post_id = request.form.get("post_id")
        status = Votes.query.filter_by(post_id=post_id, user_id=current_user.id).first()
        if status:
            if status.dislike == 1:
                status.dislike = 0
            elif status.dislike == 0:
                status.dislike = 1
                status.like = 0    
        if not status:
            dislike = Votes(post_id=post_id, user_id=current_user.id, like=0, dislike=1)
            db.session.add(dislike) 
        db.session.commit()
        likes = get_likes()
        dislikes = get_dislikes()
    return jsonify({'likes': likes,'dislikes': dislikes})


@users.route('/votes', methods=['GET', 'POST'])
@login_required
def get_votes():
    likes = get_likes()
    dislikes = get_dislikes()
    return jsonify({'likes': likes, 'dislikes': dislikes})


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

