import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail
from flaskblog.models import Votes
from collections import Counter
from flask_login import current_user


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_images', picture_fn)
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
