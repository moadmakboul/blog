import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import RegistrationForm, LoginForm, UpdateForm, PostForm, RequestResetForm, ResetPasswordForm
from flaskblog.models import User, Post, Votes
from flask_login import login_user, login_required, logout_user, current_user
from collections import Counter
from flask_mail import Message


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_images', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def get_likes():
    likes = {
        'liked_posts': {},
        'button_status': {}
    }
    votes = Votes.query.filter(Votes.like == 1)
    for vote in votes:
        likes['liked_posts'][vote.id] = vote.post_id
        if current_user.is_authenticated and current_user.id == vote.user_id:
            likes['button_status'][vote.post_id] = True
    total_votes = Counter(likes['liked_posts'].values())
    return total_votes, likes['button_status']
    
    

def get_dislikes():
    dislikes = {
        'disliked_posts': {},
        'button_status': {}
    }
    votes = Votes.query.filter(Votes.dislike == 1)
    for vote in votes:
        dislikes['disliked_posts'][vote.id] = vote.post_id
        if current_user.is_authenticated and current_user.id == vote.user_id:
            dislikes['button_status'][vote.post_id] = True
    total_votes = Counter(dislikes['disliked_posts'].values())
    return total_votes, dislikes['button_status'] 

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@blog.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    if you did not make this request then simply ignore this email and no changes will be made
    '''
    mail.send(msg)


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    likes = get_likes()
    dislikes = get_dislikes() 
    return render_template('home.html', title='Home Page', posts=posts, likes=likes, dislikes=dislikes)


@app.route('/about')
def about():
    return render_template('about.html', title='About Page')


@app.route('/register', methods=['GET', 'POST'])
def register_me():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('./auth/register.html', title='Register', form=form)

    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('./auth/login.html', title='Login', form=form)


@app.route("/profile", methods=['GET', 'POST'])
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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/post/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('New post has been created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Create Post', form=form, legend='Create post')


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    likes = get_likes()
    dislikes = get_dislikes()
    return render_template('post.html', title='Post', post=post, likes=likes, dislikes=dislikes)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user: 
        abort(403)
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    elif form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post has been updated successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Update post', form=form, legend='Update post')


@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    votes = Votes.query.filter_by(post_id=post_id).all()
    if post.author != current_user:
        abort(403)
    for vote in votes:
        db.session.delete(vote)
    db.session.delete(post)
    db.session.commit()
    flash('The post has been successfully deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/post/<string:username>', methods=['GET', 'POST'])
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    likes = get_likes()
    dislikes = get_dislikes()
    return render_template('user_posts.html', title=f'{username}\'s posts', posts=posts, user=user, likes=likes, dislikes=dislikes)


@app.route('/vote/like', methods=['GET', 'POST'])
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



@app.route('/vote/dislike', methods=['GET', 'POST'])
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


@app.route('/votes', methods=['GET', 'POST'])
@login_required
def get_votes():
    likes = get_likes()
    dislikes = get_dislikes()
    return jsonify({'likes': likes, 'dislikes': dislikes})


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

