from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from datetime import date, datetime
from functools import wraps
import article_storage
from forms import AddArticleForm, LoginForm
from config import SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

def login_required(f):
    """Decorator to require login for admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/home')
def home():
    """Display all articles on the home page"""
    articles = article_storage.get_all_articles()
    return render_template('home.html',
                           title_page='Home',
                           articles=articles)

@app.route('/article/<article_id>')
def view_article(article_id):
    """Display a single article"""
    article = article_storage.get_article(article_id)
    if not article:
        abort(404)
    return render_template('article.html',
                           title_page=article['title'],
                           article=article)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for admin"""
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == ADMIN_USERNAME and form.password.data == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('add_article'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html',
                           title_page='Login',
                           form=form)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/new', methods=['GET', 'POST'])
@login_required
def add_article():
    """Create a new article (admin only)"""
    form = AddArticleForm()
    if form.validate_on_submit():
        title = form.article_title.data
        content = form.article_content.data
        pub_date = form.publication_date.data
        
        article_id = article_storage.save_article(title, content, pub_date)
        flash(f'Article "{title}" published successfully!', 'success')
        return redirect(url_for('view_article', article_id=article_id))
    
    current_date = date.today()
    return render_template('add_article.html',
                           title_page='New article',
                           current_date=current_date,
                           form=form,
                           article=None)

@app.route('/edit/<article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    """Edit an existing article (admin only)"""
    article = article_storage.get_article(article_id)
    if not article:
        abort(404)
    
    form = AddArticleForm()
    
    if form.validate_on_submit():
        title = form.article_title.data
        content = form.article_content.data
        pub_date = form.publication_date.data
        
        success = article_storage.update_article(article_id, title, content, pub_date)
        if success:
            flash(f'Article "{title}" updated successfully!', 'success')
            return redirect(url_for('view_article', article_id=article_id))
        else:
            flash('Error updating article.', 'danger')
    else:
        # Pre-populate form with existing article data (for GET request or after validation error)
        form.article_title.data = article['title']
        form.article_content.data = article['content']
        # Parse the publication_date string back to a date object
        pub_date_str = article['publication_date'][:10]  # Get YYYY-MM-DD part
        try:
            form.publication_date.data = datetime.strptime(pub_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            form.publication_date.data = date.today()
    
    return render_template('add_article.html',
                           title_page='Edit article',
                           current_date=date.today(),
                           form=form,
                           article=article,
                           is_edit=True)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html', title_page='Page Not Found'), 404

if __name__ == '__main__':
    app.run(debug=True) 

