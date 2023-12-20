# routes.py

from flask import abort, render_template, request, url_for, flash, redirect
from .forms import RegistrationForm, LoginForm, StorageForm
from .models import User, Storage
from .extensions import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required



def configure_routes(app):

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        return render_template('login.html', title='Login', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('home'))
    
    @app.route('/storage/new', methods=['GET', 'POST'])
    @login_required
    def new_storage():
     form = StorageForm()
     if form.validate_on_submit():
        storage_type = request.form.get('storage_type')
        storage = Storage(name=form.name.data, user_id=current_user.id)

        # Define capacity based on storage type
        if storage_type == 'small':
            storage.capacity = 128  # Let's say small storage is 128 units
            flash('Small storage created!', 'success')
        elif storage_type == 'central':
            storage.capacity = 1024  # And central storage is 1024 units
            flash('Central storage created!', 'success')
        
        db.session.add(storage)
        db.session.commit()
        return redirect(url_for('view_storages'))  # Redirect to the storage overview
        
     return render_template('create_storage.html', form=form)
    
    @app.route('/main_storage')
    @login_required
    def main_storage():
     storage_items = Storage.query.filter_by(user_id=current_user.id).all()
     return render_template('main_storage.html', storage_items=storage_items)
    
    @app.route('/storages')
    @login_required
    def view_storages():
     storages = Storage.query.filter_by(user_id=current_user.id).all()
     return render_template('view_storages.html', storages=storages)