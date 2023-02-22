from datetime import datetime 
from itsdangerous import TimedSerializer as Serializer
from flaskblog import db, login_manager
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin, AnonymousUserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    password = db.Column(db.String(100), nullable=False)
    joined_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)
    votes = db.relationship('Votes', backref='voter', lazy=True)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)
    

    def __repr__(self) -> str:
        return super().__repr__(f'User: {self.username}, {self.email}, {self.image_file}')
    

        

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    votes = db.relationship('Votes', backref='post', lazy=True)



    def __repr__(self) -> str:
        return super().__repr__(f'Post: {self.title}, {self.date_posted}')
    

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    like = db.Column(db.Integer, default=0)
    dislike = db.Column(db.Integer, default=0)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    def __repr__(self) -> str:
        return super().__repr__(f'Post: {self.post_id} {self.like} {self.dislike}')
   


    


     
        






