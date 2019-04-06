"""Routes for authentication."""

from flask import flash, redirect, url_for, render_template, request
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.urls import url_parse
from app.auth import bp
from app.auth.forms import LoginForm
from app.auth.models import Admin

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page route."""

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin is None or not admin.check_password(form.password.data):
            flash('Unknown user or invalid password!', 'danger')
            return redirect(url_for('auth.login'))
        else:
            login_user(admin, remember=form.remember_me)

            next_page = request.args.get('next')

            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.index')

            return redirect(next_page)

    return render_template('login.html', title='Sign in', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Logout the user."""

    logout_user()

    return redirect(url_for('main.index'))
