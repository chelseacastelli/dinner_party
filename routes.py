

from re import L
from forms import *
from models import *
from app import app, db, login_manager

from flask import render_template, request, redirect, url_for, flash
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
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required   # protects user route
def user(username):
  user = User.query.filter_by(username=username).first_or_404()
  dinner_parties = DinnerParty.query.filter_by(party_host_id=user.id)

  if dinner_parties is None:
    dinner_parties = []

  form = DinnerPartyForm(csrf_enabled=False)

  if form.validate_on_submit():
    new_dinner_party = DinnerParty(
      date=form.date.data,
      venue=form.venue.data,
      main_dish=form.main_dish.data,
      number_seats=int(form.number_seats.data),
      party_host_id=user.id,
      attendees=username)
    
    db.session.add(new_dinner_party)
    db.session.commit()

  return render_template('user.html', user=user, dinner_parties=dinner_parties, form=form)


@app.route('/user/<username>/rsvp/', methods=['GET', 'POST'])
@login_required
def rsvp(username):
  user = User.query.filter_by(username=username).first_or_404()
  dinner_parties = DinnerParty.query.all()

  if dinner_parties is None:
    dinner_parties = []

  form = RsvpForm(csrf_enabled=False)

  if form.validate_on_submit():
    dinner_party = DinnerParty.query.filter_by(id=int(form.party_id.data)).first()

    try:
      dinner_party.attendees += f', {username}'
      db.session.commit()

      # find the host of dinner_party
      host = User.query.filter_by(int(dinner_party.party_host_id)).first()
      flash(f"You successfully RSVP'd to {host.username}'s dinner party on {dinner_party.date}!")

    except:
      flash("Please enter a valid Party ID to RSVP!")

  return render_template('rsvp.html', user=user, dinner_parties=dinner_parties, form=form)


# landing page route
@app.route('/')
def index():
  # grab all guests and display them
  current_users = User.query.all()
  return render_template('landing_page.html', current_users = current_users)

