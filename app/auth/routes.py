from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.auth.services import AuthService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        success, message = AuthService.register_user(
            username=request.form.get('username'),
            email=request.form.get('email'),
            password=request.form.get('password')
        )

        flash(message, 'success' if success else 'error')
        if success:
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        success, message, user = AuthService.authenticate_user(
            username=request.form.get('username'),
            password=request.form.get('password')
        )

        if success and user:
            login_user(user)
            return redirect(url_for('vms.list_vms'))

        flash(message, 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out', 'success')
    return redirect(url_for('auth.login'))