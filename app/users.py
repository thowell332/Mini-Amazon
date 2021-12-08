from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l

from .models.user import User
from .models.userReviews import userProductReview, userSellerReview
from .models.sellerReviews import sellerReviewSummary, sellerReview
from .models.productReviews import productReviewSummary, productReview

from flask import Blueprint
bp = Blueprint('users', __name__)


@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user_info = User.get(current_user.id)
    seller_status = User.sellerStatus(current_user.id)
    return render_template('account.html', title = 'Profile', user_info = user_info, seller_status = seller_status)

class UpdateProfile(FlaskForm):
    firstname = StringField(_l('First Name'), validators=[DataRequired()])
    lastname = StringField(_l('Last Name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    address = StringField(_l('Address (Street, Apt #, City, State, Zip)'), validators=[DataRequired()])        
    submit = SubmitField(_l('Register'))

@bp.route('/updateprofile', methods=['GET', 'POST'])
def updateProfile():
    user_info = User.get(current_user.id)
    form = UpdateProfile(obj = user_info)
    if form.validate_on_submit():
        if User.updateProfile(user_info.id, 
                                form.email.data, 
                                form.firstname.data, 
                                form.lastname.data, 
                                form.address.data):
            flash('Congratulations, you have updated your account information!')
            return redirect(url_for('users.profile'))
    return render_template('updateProfile.html', title='Update Profile', form=form)

class UpdatePassword(FlaskForm):
    password = PasswordField(_l('New Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm New Password'), validators=[DataRequired(), EqualTo('password')])           
    submit = SubmitField(_l('Update'))

@bp.route('/updatepassword', methods=['GET', 'POST'])
def updatePassword():
    form = UpdatePassword()
    if form.validate_on_submit():
        if User.updatePassword(current_user.id, form.password.data):
            flash('Congratulations, you have successfully updated your password!')
            return redirect(url_for('users.profile'))
    return render_template('updatePassword.html', title='Update Password', form=form)

@bp.route('/becomeseller', methods=['GET','POST'])
def becomeSeller():
    if User.becomeSeller(current_user.id):
        flash('Congratuations, you have successfully become a seller!')
        return redirect(url_for('users.profile'))
    else:
        flash('Something went wrong, please try again!')
        return redirect(url_for('users.profile'))


class BalanceForm(FlaskForm):
    withdraw = FloatField(_l('How much do you want to withdraw'), default = 0)
    deposit = FloatField(_l('How much do you want to deposit'), default = 0)
    submit = SubmitField(_l('Update'))

@bp.route('/updatebalance', methods=['GET', 'POST'])
def updateBalance():
    curr_balance = User.get_balance(current_user.id)
    form = BalanceForm()
    if form.validate_on_submit():
        if form.withdraw.data > float(curr_balance):
            flash('You cannot withdraw more than your current balance')
            return redirect(url_for('users.updateBalance'))
        else:
            new_balance = float(curr_balance) - form.withdraw.data
            new_balance = float(new_balance) + form.deposit.data
            User.update_balance(current_user.id, new_balance)
            return redirect(url_for('users.profile'))
    return render_template('balance.html', title='Balance', form=form, curr_balance=curr_balance)
        
class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField(_l('First Name'), validators=[DataRequired()])
    lastname = StringField(_l('Last Name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    address = StringField(_l('Address (Street, Apt #, City, State, Zip)'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError(_('Already a user with this email.'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.address.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

"""
class UserReviewForm(FlaskForm):
    review = StringField(_l('Review'), validators=[DataRequired()])
"""


@bp.route('/userReviews')
def userReviews():
    # get all product reviews user has made:
    productReviews = userProductReview.get('5') #CHANGE '5' TO CURRENT USER ID
    sellerReviews = userSellerReview.get('5') #CHANGE '5' TO CURRENT USER ID
    # render the page by adding information to the index.html file
    return render_template('userReviews.html',
                           userProductReviews=productReviews, userSellerReviews=sellerReviews)


@bp.route('/sellerReviews')
def sellerReviews():
    # get all reviews for given seller:
    summary = sellerReviewSummary.get('2') #CHANGE '2' TO SELECTED SELLER ID
    reviews = sellerReview.get('2') #CHANGE '2' TO SELECTED SELLER ID
    # render the page by adding information to the index.html file
    return render_template('sellerSummaryReviews.html',
                           sellerReviewSummary=summary, sellerReviews=reviews)
  
   
@bp.route('/productReviews')
def productReviews():
    # get all reviews for given seller:
    summary = productReviewSummary.get('2') #CHANGE '2' TO SELECTED PRODUCT ID
    reviews = productReview.get('2') #CHANGE '2' TO SELECTED PRODUCT ID
    # render the page by adding information to the index.html file
    return render_template('productSummaryReviews.html',
                           productReviewSummary=summary, productReviews=reviews)

class EditReviewForm(FlaskForm):
    numStars= StringField(_l('Number of Stars'), validators=[DataRequired()])
    description = StringField(_l('Review'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

@bp.route('/editReview', methods=['GET', 'POST'])
def editReview():
    form = EditReviewForm()
    if form.validate_on_submit():
        print("hi")
        userProductReview.update_product_review('5', '1', form.numStars.data, '10/20/21 0:00', form.description.data)
        userSellerReview.update_seller_review('5', '2', form.numStars.data, '10/20/21 0:00', form.description.data)
        flash('Review has been updated')
        return redirect(url_for('users.userReviews'))
    # render the page by adding information to the index.html file
    return render_template('editReview.html', title='Edit Review', form=form)
   
   
