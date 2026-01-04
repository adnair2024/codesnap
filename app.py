import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Snippet, Vote, AdminLog
from sqlalchemy import func, text

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Robust DATABASE_URL handling
db_url = os.environ.get('DATABASE_URL', '').strip().strip('"').strip("'")
if not db_url:
    db_url = 'sqlite:///snippets.db'

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,  # Checks connection health before every query
    "pool_recycle": 300,    # Refreshes connections every 5 minutes to prevent SSL timeout
    "pool_size": 5,         # Limits local connections to help with "Max Connections" issues
    "max_overflow": 0,      # Prevents app from creating extra connections beyond pool_size
}

db.init_app(app)

# Ensure tables are created on startup
with app.app_context():
    db.create_all()
    # Migration hack: Increase password_hash length for existing tables
    try:
        db.session.execute(text('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(256)'))
        db.session.commit()
    except Exception:
        db.session.rollback()
    
    # Migration hack: Add is_moderator column if not exists
    try:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN is_moderator BOOLEAN DEFAULT FALSE'))
        db.session.commit()
    except Exception:
        db.session.rollback()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.template_filter('flag')
def flag_filter(country_name):
    flags = {
        'USA': '🇺🇸',
        'Canada': '🇨🇦',
        'UK': '🇬🇧',
        'Germany': '🇩🇪',
        'France': '🇫🇷',
        'India': '🇮🇳',
        'Japan': '🇯🇵',
        'Australia': '🇦🇺',
        'Brazil': '🇧🇷',
        'China': '🇨🇳',
        'Unknown': '❓'
    }
    return flags.get(country_name, '❓')

@app.context_processor
def utility_processor():
    def verified_badge(user_id):
        # We need to fetch the user if we only have ID, or expect a user object.
        # Given existing usage verified_badge(user.id), let's handle both.
        user = User.query.get(user_id)
        if not user:
            return ''
            
        if user.id == 1:
            # Admin Badge (Gold/Shield)
            return '<span class="text-warning ms-1" title="Admin" style="vertical-align: text-bottom;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-shield-fill-check" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 0c-.69 0-1.843.265-2.928.56-1.11.3-2.229.655-2.887.87a1.54 1.54 0 0 0-1.044 1.262c-.596 4.477.787 7.795 2.465 9.99a11.775 11.775 0 0 0 3.32 3.133c.336.21.722.333 1.074.333s.738-.123 1.074-.333a11.775 11.775 0 0 0 3.32-3.133c1.678-2.195 3.061-5.513 2.465-9.99a1.541 1.541 0 0 0-1.044-1.263 62.467 62.467 0 0 0-2.887-.87C9.843.266 8.69 0 8 0zm2.146 5.146a.5.5 0 0 1 .708.708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7.5 7.793l2.646-2.647z"/></svg></span>'
        elif user.is_moderator:
            # Moderator Badge (Blue/Check)
            return '<span class="text-info ms-1" title="Moderator" style="vertical-align: text-bottom;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-patch-check-fill" viewBox="0 0 16 16"><path d="M10.067.87a2.89 2.89 0 0 0-4.134 0l-.622.638-.896.011a2.89 2.89 0 0 0-2.924 2.924l.01.896-.636.622a2.89 2.89 0 0 0 0 4.134l.638.622-.011.896a2.89 2.89 0 0 0 2.924 2.924l.896-.01.622.636a2.89 2.89 0 0 0 4.134 0l.622-.637.896-.011a2.89 2.89 0 0 0 2.924-2.924l-.01-.896.636-.622a2.89 2.89 0 0 0 0-4.134l-.637-.622.011-.896a2.89 2.89 0 0 0-2.924-2.924l-.896.01-.622-.636zm.287 5.984-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7 8.793l2.646-2.647a.5.5 0 0 1 .708.708z"/></svg></span>'
        return ''
    return dict(verified_badge=verified_badge)

@app.route('/')
def index():
    public_snippets = Snippet.query.filter_by(is_public=True).order_by(Snippet.created_at.desc()).limit(10).all()
    return render_template('index.html', snippets=public_snippets)

@app.get("/health")
def health_check():
    return {"status": "alive"}, 200

def log_action(action, details=None, user_id=None):
    # Use provided user_id or current_user's id
    u_id = user_id or (current_user.id if current_user.is_authenticated else None)
    log = AdminLog(admin_id=u_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            log_action("Login", f"User {username} logged in")
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        country = request.form.get('country', 'Unknown')
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
        else:
            user = User(username=username, country=country)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            log_action("Register", f"New user registered: {username}", user_id=user.id)
            login_user(user)
            return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    log_action("Logout", f"User {current_user.username} logged out")
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Determine visibility filter
    if current_user.is_authenticated and current_user.id == user.id:
        filter_kwargs = {'user_id': user.id}
    else:
        filter_kwargs = {'user_id': user.id, 'is_public': True}
    
    # Fetch snippets
    snippets = Snippet.query.filter_by(**filter_kwargs).order_by(Snippet.created_at.desc()).all()
    
    # Calculate stats
    snippet_count = len(snippets)
    
    # Calculate total score using aggregation
    if snippets:
        # Join Vote -> Snippet to filter by snippet criteria
        total_score = db.session.query(func.sum(Vote.value))\
            .join(Snippet)\
            .filter(Snippet.user_id == user.id)\
            .filter(Snippet.id.in_([s.id for s in snippets]))\
            .filter(Vote.value == 1)\
            .scalar() or 0
    else:
        total_score = 0
        
    return render_template('profile.html', user=user, snippets=snippets, snippet_count=snippet_count, total_score=total_score)

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
        log_action("Create Snippet", f"Created snippet '{title}'")
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
        log_action("Edit Snippet", f"Edited snippet '{snippet.title}'")
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
    log_action("Toggle Privacy", f"Snippet '{snippet.title}' is now {'Public' if snippet.is_public else 'Private'}")
    return redirect(request.referrer or url_for('profile', username=current_user.username))

@app.route('/snippet/<int:snippet_id>/delete', methods=['POST'])
@login_required
def delete_snippet(snippet_id):
    snippet = Snippet.query.get_or_404(snippet_id)
    
    # Check if owner, admin, or moderator
    is_admin = current_user.id == 1
    is_mod = current_user.is_moderator
    
    if snippet.owner != current_user and not is_admin and not is_mod:
        flash('You do not have permission to delete this snippet.')
        return redirect(url_for('index'))
    
    title = snippet.title
    owner_name = snippet.owner.username
    
    db.session.delete(snippet)
    db.session.commit()
    
    # Log if deleted by staff
    if (is_admin or is_mod) and snippet.owner != current_user:
        log_action("Staff Delete Snippet", f"Deleted snippet '{title}' owned by {owner_name}")
        flash(f'Snippet "{title}" deleted by staff.')
    else:
        log_action("Delete Snippet", f"Deleted snippet '{title}'")
        flash(f'Snippet "{title}" deleted.')
        
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

@app.route('/stats')
def stats():
    # 1. Total Users
    user_count = User.query.count()
    
    # 2. Top 10 Users by Snippet Count
    top_snippet_users = db.session.query(
        User.username, 
        User.country,
        User.id,
        User.is_moderator,
        func.count(Snippet.id).label('count')
    ).join(Snippet).group_by(User.id).order_by(text('count DESC')).limit(10).all()
    
    # 3. Top 10 Users by Reputation (Sum of votes on their snippets)
    # logic: User -> Snippet -> Vote. Sum(Vote.value)
    top_reputation_users = db.session.query(
        User.username,
        User.country,
        User.id,
        User.is_moderator,
        func.sum(Vote.value).label('reputation')
    ).join(Snippet, Snippet.user_id == User.id)\
     .join(Vote, Vote.snippet_id == Snippet.id)\
     .group_by(User.id)\
     .order_by(text('reputation DESC'))\
     .limit(10).all()
     
    # 4. Users by Country
    country_stats = db.session.query(
        User.country,
        func.count(User.id).label('count')
    ).group_by(User.country).all()
    
    # Format data for Chart.js
    country_labels = [stat[0] for stat in country_stats]
    country_data = [stat[1] for stat in country_stats]
    
    return render_template(
        'stats.html', 
        user_count=user_count,
        top_snippet_users=top_snippet_users,
        top_reputation_users=top_reputation_users,
        country_labels=country_labels,
        country_data=country_data
    )

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.id != 1:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    users = User.query.all()
    logs = AdminLog.query.order_by(AdminLog.timestamp.desc()).all()
    return render_template('admin.html', users=users, logs=logs)

@app.route('/admin/verify/<int:user_id>', methods=['POST'])
@login_required
def admin_verify_user(user_id):
    if current_user.id != 1:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    if user.id == 1:
        flash('Admin is always verified.')
        return redirect(url_for('admin_dashboard'))

    # Toggle moderator status
    user.is_moderator = not user.is_moderator
    db.session.commit()
    
    status = "Verified/Moderator" if user.is_moderator else "Unverified"
    log_action("Toggle Verify User", f"Changed {user.username} (ID: {user.id}) status to {status}")
    
    flash(f'User {user.username} is now {status}')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.id != 1:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    if user_id == 1:
        flash('Cannot delete admin user')
        return redirect(url_for('admin_dashboard'))
        
    user = User.query.get_or_404(user_id)
    username = user.username
    user_id_val = user.id
    
    db.session.delete(user)
    db.session.commit()
    
    log_action("Admin Delete User", f"Admin deleted user {username} (ID: {user_id_val})")
    flash(f'User {username} deleted')
    return redirect(url_for('admin_dashboard'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        country = request.form.get('country')
        
        user = User.query.get(current_user.id)
        
        # Username change
        if new_username and new_username != user.username:
            if User.query.filter_by(username=new_username).first():
                flash('Username already exists')
                return redirect(url_for('settings'))
            old_name = user.username
            user.username = new_username
            log_action("Update Profile", f"Username changed from {old_name} to {new_username}")
            
        # Password change
        if new_password:
            user.set_password(new_password)
            log_action("Update Profile", "Password changed")
            
        # Country change
        if country and country != user.country:
            old_country = user.country
            user.country = country
            log_action("Update Profile", f"Country changed from {old_country} to {country}")
            
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile', username=user.username))
    
    user_logs = AdminLog.query.filter_by(admin_id=current_user.id).order_by(AdminLog.timestamp.desc()).all()
    return render_template('settings.html', logs=user_logs)

@app.route('/settings/delete', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    username = user.username
    log_action("Delete Account", f"User {username} deleted their own account")
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Your account has been permanently deleted.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
