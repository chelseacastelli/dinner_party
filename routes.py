

from forms import *
from models import *
from app import app, db, login_manager

from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse


# registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegistrationForm(csrf_enabled=False)
  if form.validate_on_submit():
    # define user with data from form here:
    user = User(username = form.username.data, email = form.email.data)
    # set user's password here:
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('register'))

  return render_template('register.html', title='Register', form=form)

# helper function -- loads user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(csrf_enabled=False)

    if form.validate_on_submit():   # if form validates
      user = User.query.filter_by(email=form.email.data).first()    # query User table for the user with given email

      if user and user.check_password(form.password.data):    # check that form data entered is correct
        # login user and redirect to either next_page or index
        login_user(user, remember=form.remember.data)   
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index', _external=True, _scheme='https'))
     
      # user not found, redirect to login page
      else:
        return redirect(url_for('login', _external=True, _scheme='https'))

    return render_template('login.html', form=form)

# user profile route
@app.route('/user/<username>')
@login_required   # protects user route
def user(username):
  user = User.query.filter_by(username=username).first_or_404()
  return render_template('user.html', user=user)

# landing page route
@app.route('/')
def index():
  # grab all guests and display them
  current_users = User.query.all()
  return render_template('landing_page.html', current_users = current_users)