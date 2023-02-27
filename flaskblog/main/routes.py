from flask import render_template, request
from flaskblog.models import Post
from flask import Blueprint
from flaskblog.users.utils import get_likes, get_dislikes


main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    latest_post = Post.query.order_by(Post.date_posted.desc()).first()
    likes = get_likes()
    dislikes = get_dislikes()
    return render_template('home.html', title='Home Page', posts=posts, likes=likes, dislikes=dislikes, latest_post=latest_post.title)


@main.route('/about')
def about():
    return render_template('about.html', title='About Page')
