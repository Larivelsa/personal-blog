from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, PasswordField
from wtforms.validators import DataRequired

class AddArticleForm(FlaskForm):
    article_title = StringField('Article Title', validators=[DataRequired()])
    publication_date = DateField('Publication Date', validators=[DataRequired()])
    article_content = TextAreaField('Article Content', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])