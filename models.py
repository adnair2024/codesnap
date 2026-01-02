from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    snippets = db.relationship('Snippet', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Snippet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), default='javascript')
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    votes = db.relationship('Vote', backref='snippet', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def score(self):
        return sum(vote.value for vote in self.votes)

    def get_user_vote(self, user_id):
        return self.votes.filter_by(user_id=user_id).first()

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    snippet_id = db.Column(db.Integer, db.ForeignKey('snippet.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False) # 1 for upvote, -1 for downvote

    __table_args__ = (db.UniqueConstraint('user_id', 'snippet_id', name='_user_snippet_uc'),)
