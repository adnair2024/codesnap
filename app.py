import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Snippet, Vote

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///snippets.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    public_snippets = Snippet.query.filter_by(is_public=True).order_by(Snippet.created_at.desc()).limit(10).all()
    return render_template('index.html', snippets=public_snippets)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_authenticated and current_user.id == user.id:
        snippets = Snippet.query.filter_by(user_id=user.id).order_by(Snippet.created_at.desc()).all()
    else:
        snippets = Snippet.query.filter_by(user_id=user.id, is_public=True).order_by(Snippet.created_at.desc()).all()
    return render_template('profile.html', user=user, snippets=snippets)

@app.route('/vote/<int:snippet_id>/<action>', methods=['POST'])
@login_required
def vote(snippet_id, action):
    snippet = Snippet.query.get_or_404(snippet_id)
    if not snippet.is_public and snippet.owner != current_user:
        return "Unauthorized", 403
    
    vote = Vote.query.filter_by(user_id=current_user.id, snippet_id=snippet_id).first()
    value = 1 if action == 'up' else -1

    if vote:
        if vote.value == value:
            # User clicked same button -> remove vote (toggle off)
            db.session.delete(vote)
        else:
            # Change vote
            vote.value = value
    else:
        # New vote
        new_vote = Vote(user_id=current_user.id, snippet_id=snippet_id, value=value)
        db.session.add(new_vote)
    
    db.session.commit()
    # If request is AJAX, return JSON, else redirect
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'score': snippet.score}
    return redirect(request.referrer or url_for('index'))

@app.route('/snippet/new', methods=['GET', 'POST'])
@login_required
def new_snippet():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        language = request.form.get('language')
        is_public = request.form.get('is_public') == 'on'
        snippet = Snippet(title=title, content=content, language=language, is_public=is_public, owner=current_user)
        db.session.add(snippet)
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username))
    return render_template('snippet_edit.html', snippet=None)

@app.route('/snippet/<int:snippet_id>')
def view_snippet(snippet_id):
    snippet = Snippet.query.get_or_404(snippet_id)
    if not snippet.is_public and (not current_user.is_authenticated or snippet.owner != current_user):
        return "Unauthorized", 403
    return render_template('snippet_view.html', snippet=snippet)

@app.route('/snippet/<int:snippet_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_snippet(snippet_id):
    snippet = Snippet.query.get_or_404(snippet_id)
    if snippet.owner != current_user:
        flash('You do not have permission to edit this snippet.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        snippet.title = request.form.get('title')
        snippet.content = request.form.get('content')
        snippet.language = request.form.get('language')
        snippet.is_public = request.form.get('is_public') == 'on'
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username))
        
    return render_template('snippet_edit.html', snippet=snippet)

@app.route('/snippet/<int:snippet_id>/toggle_privacy')
@login_required
def toggle_privacy(snippet_id):
    snippet = Snippet.query.get_or_404(snippet_id)
    if snippet.owner != current_user:
        flash('Unauthorized')
        return redirect(url_for('index'))
    snippet.is_public = not snippet.is_public
    db.session.commit()
    return redirect(request.referrer or url_for('profile', username=current_user.username))

@app.route('/snippet/<int:snippet_id>/delete', methods=['POST'])
@login_required
def delete_snippet(snippet_id):
    snippet = Snippet.query.get_or_404(snippet_id)
    if snippet.owner != current_user:
        flash('You do not have permission to delete this snippet.')
        return redirect(url_for('index'))
    db.session.delete(snippet)
    db.session.commit()
    return redirect(url_for('profile', username=current_user.username))

@app.route('/search')
def search_users():
    query = request.args.get('q')
    if query:
        # Exact match redirect
        user = User.query.filter_by(username=query).first()
        if user:
            return redirect(url_for('profile', username=user.username))
        # Partial match list (simplified for now, just flash and redirect home if not found)
        users = User.query.filter(User.username.contains(query)).all()
        if len(users) == 1:
             return redirect(url_for('profile', username=users[0].username))
        elif users:
            # We don't have a search results page, so for now let's just pick the first one or show a message.
            # To be more useful, let's create a simple search results template or just redirect to the first match.
            # Given constraints, I'll redirect to the first match but flash "Found X users"
            flash(f'Found {len(users)} users. Redirecting to {users[0].username}.')
            return redirect(url_for('profile', username=users[0].username))
            
        flash(f'No user found with name containing "{query}"')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
