from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import db
from flaskblog.posts.forms import PostForm
from flaskblog.models import User, Post, Votes
from flask_login import login_required, current_user
from flask import Blueprint
from flaskblog.users.utils import get_likes, get_dislikes

posts = Blueprint('posts', __name__)


@posts.route("/post/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('New post has been created successfully!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='Create Post', form=form, legend='Create post')


@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    likes = get_likes()
    dislikes = get_dislikes()
    return render_template('post.html', title='Post', post=post, likes=likes, dislikes=dislikes)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='Update post', form=form, legend='Update post')


@posts.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
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
    return redirect(url_for('main.home'))


@posts.route('/post/<string:username>', methods=['GET', 'POST'])
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    likes = get_likes()
    dislikes = get_dislikes()
    return render_template('user_posts.html', title=f'{username}\'s posts', posts=posts, user=user, likes=likes, dislikes=dislikes)
