__author__ = 'Martin'
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, login_required, logout_user, current_user

from .. import db
from ..models import User
from . import auth
from .forms import LoginForm, RegistrationForm, PasswordResetForm, EmailResetForm
from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm your account', 'auth/email/confirm', user=user, token=token)
        flash('You have registered successfully, check your email for verification')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account!')
    else:
        flash('Your confirmation link is invalid or expired')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '<Flasky email confirmation>', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    form = PasswordResetForm()
    user = User.query.filter_by(email=current_user.email).first()
    if form.validate_on_submit():
        if user.verify_password(form.current_pass.data):
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash('Password has been changed!')
            return redirect(url_for('main.index'))
        flash('Your current password was not correct')
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset_email', methods=['GET', 'POST'])
@login_required
def send_reset_email():
    form = EmailResetForm()
    user = User.query.filter_by(email=current_user.email).first()
    if form.validate_on_submit():
        token = user.generate_reset_token(new_email=form.email.data)
        send_email(form.old_email.data, '<FLASKY> email reset', '/auth/email/email_reset', user=user, token=token)
        flash('We have sent you an email to verify your email change')
        return redirect(url_for('main.index'))
    return render_template('auth/reset_email.html', form=form)

@auth.route('/reset_email/<token>')
@login_required
def reset_email(token):
    if current_user.reset_email(token):
        flash('Email has been set to new email')
        logout_user()
    else:
        flash('Email reset unsuccessful. Try again')
    return redirect(url_for('main.index'))