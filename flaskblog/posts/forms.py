from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length



class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=120)])
    content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

