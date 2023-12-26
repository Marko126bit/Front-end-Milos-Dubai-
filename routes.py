# routes.py

from http.client import FORBIDDEN
from flask import abort, render_template, request, url_for, flash, redirect
from .forms import RegistrationForm, LoginForm, StorageForm
from .models import User, Storage
from .extensions import db, bcrypt, cache
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
        if storage_type == 'small':
            # Logic to create small storage
            flash('Small storage created!', 'success')
        elif storage_type == 'central':
            # Logic to create central storage
            flash('Central storage created!', 'success')
        # Assuming the Storage model has a 'name' field and a foreign key 'user_id'
        storage = Storage(name=form.name.data, user_id=current_user.id)
        db.session.add(storage)
        db.session.commit()
        return redirect(url_for('view_storages'))  # Adjust to the correct route
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
     return render_template('view_storage.html', storages=storages)

    @app.errorhandler(403)
    def forbidden(e):
     return render_template('403.html'), 403  # Ensure you have a 403.html template

    @app.route('/edit_storage/<int:storage_id>', methods=['GET', 'POST'])
    @login_required
    def edit_storage(storage_id):
     storage = Storage.query.get_or_404(storage_id)
     if storage.user_id != current_user.id:
        abort(403)  # HTTP Forbidden status code
    # Present a form and handle editing the storage
    # return render_template('edit_storage.html', storage=storage)

    @app.route('/delete_storage/<int:storage_id>')
    @login_required
    def delete_storage(storage_id):
     storage = Storage.query.get_or_404(storage_id)
     if storage.user_id != current_user.id:
        abort(403)  # HTTP Forbidden status code
     db.session.delete(storage)
     db.session.commit()
     flash('Storage deleted successfully', 'success')
     return redirect(url_for('view_storages'))
