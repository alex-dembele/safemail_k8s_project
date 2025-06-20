import os
from flask import Flask, redirect, url_for, request, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import argon2
import click

db = SQLAlchemy()
login_manager = LoginManager()

def build_database_uri():
    """Construit l'URI de la base de données à partir des variables d'environnement NXH_*."""
    user = os.environ.get('NXH_DATABASE_USER')
    password = os.environ.get('NXH_DATABASE_PASSWORD')
    host = os.environ.get('NXH_DATABASE_HOST')
    port = os.environ.get('NXH_DATABASE_PORT')
    dbname = os.environ.get('NXH_DATABASE_NAME')

    if not all([user, password, host, port, dbname]):
        raise ValueError("Une ou plusieurs variables d'environnement de base de données NXH_* sont manquantes.")

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"

# --- Définition des modèles (identique au script précédent) ---
class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    def set_password(self, password): self.password = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password, password)

class Domain(db.Model):
    __tablename__ = 'virtual_domains'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    def __str__(self): return self.name

class User(db.Model):
    __tablename__ = 'virtual_users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('virtual_domains.id'), nullable=False)
    domain = db.relationship('Domain', backref=db.backref('users', lazy=True, cascade="all, delete-orphan"))
    def set_password(self, password): self.password = argon2.using(rounds=12).hash(password)

class Alias(db.Model):
    __tablename__ = 'virtual_aliases'
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('virtual_domains.id'), nullable=False)
    domain = db.relationship('Domain', backref=db.backref('aliases', lazy=True, cascade="all, delete-orphan"))

# --- Vues Flask-Admin (identiques au script précédent) ---
class AuthModelView(ModelView):
    def is_accessible(self): return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs): return redirect(url_for('admin.login', next=request.url))

class UserAdminView(AuthModelView):
    column_list = ('email', 'domain')
    form_columns = ('email', 'domain', 'new_password')
    column_searchable_list = ['email']
    column_filters = ['domain']
    form_extra_fields = {'new_password': {'label': 'Password (laisser vide pour ne pas changer)', 'type': 'password'}}
    def on_model_change(self, form, model, is_created):
        if form.new_password.data: model.set_password(form.new_password.data)

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated: return redirect(url_for('.login'))
        return super(MyAdminIndexView, self).index()
    @expose('/login', methods=['GET', 'POST'])
    def login(self):
        if request.method == 'POST':
            user = AdminUser.query.filter_by(username=request.form.get('username')).first()
            if user and user.check_password(request.form.get('password')):
                login_user(user); return redirect(url_for('.index'))
            else:
                flash('Identifiants invalides.', 'error')
        return render_template('admin/login.html')
    @expose('/logout')
    def logout(self): logout_user(); return redirect(url_for('.index'))

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = os.environ.get('NXH_FLASK_SECRET_KEY', 'default-secret-key-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = build_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    db.init_app(app)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id): return AdminUser.query.get(int(user_id))

    admin = Admin(app, name='SafeMail Admin', template_mode='bootstrap3', index_view=MyAdminIndexView(url='/admin'))
    admin.add_view(AuthModelView(Domain, db.session, category='Gestion Email'))
    admin.add_view(UserAdminView(User, db.session, category='Gestion Email'))
    admin.add_view(AuthModelView(Alias, db.session, category='Gestion Email'))
    
    @app.cli.command("create-admin")
    @click.option("--username", required=True)
    @click.option("--email", required=True)
    @click.option("--password", required=True)
    def create_admin(username, email, password):
        """Crée l'utilisateur admin initial."""
        with app.app_context():
            if AdminUser.query.filter_by(username=username).first():
                print(f"L'utilisateur admin '{username}' existe déjà.")
                return
            user = AdminUser(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Utilisateur admin '{username}' créé avec succès.")

    @app.route("/")
    def index():
        return '<h1>Bienvenue sur le serveur SafeMail. Accédez à <a href="/admin">/admin</a> pour la gestion.</h1>'

    return app
