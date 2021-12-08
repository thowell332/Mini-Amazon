from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from datetime import datetime

from .models.user import User, UserView
from .models.userReviews import userProductReview, userSellerReview
from .models.sellerReviews import sellerReview
from .models.productReviews import productReview
from flask_paginate import Pagination, get_page_parameter

from flask import Blueprint
bp = Blueprint('users', __name__)

@bp.route('/users', methods=['GET','POST'])
def userPublicView():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    start = (page - 1) * per_page
    users = UserView.getUsersPublicView()
    pagination = Pagination(page=page, per_page=per_page, total=len(users), record_name='users')
    return render_template('usersPublic.html', users = users[start: start + per_page], pagination=pagination)
    
class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user_info = User.get(current_user.id)
    user_info.balance = round(user_info.balance, 2)
    seller_status = User.sellerStatus(current_user.id)
    return render_template('account.html', title = 'Profile', user_info = user_info, seller_status = seller_status)

class UpdateProfile(FlaskForm):
    firstname = StringField(_l('First Name'), validators=[DataRequired()])
    lastname = StringField(_l('Last Name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    address = StringField(_l('Address (Street, Apt #, City, State, Zip)'), validators=[DataRequired()])        
    submit = SubmitField(_l('Update'))

@bp.route('/updateprofile', methods=['GET', 'POST'])
def updateProfile():
    user_info = User.get(current_user.id)
    seller_status = User.sellerStatus(current_user.id)
    form = UpdateProfile(obj = user_info)
    if form.validate_on_submit():
        if User.updateProfile(user_info.id, 
                                form.email.data, 
                                form.firstname.data, 
                                form.lastname.data, 
                                form.address.data):
            flash('Congratulations, you have updated your account information!')
            return redirect(url_for('users.profile'))
    return render_template('updateProfile.html', title='Update Profile', form=form, seller_status=seller_status)

class UpdatePassword(FlaskForm):
    password = PasswordField(_l('New Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm New Password'), validators=[DataRequired(), EqualTo('password')])           
    submit = SubmitField(_l('Update'))

@bp.route('/updatepassword', methods=['GET', 'POST'])
def updatePassword():
    seller_status = User.sellerStatus(current_user.id)
    form = UpdatePassword()
    if form.validate_on_submit():
        if User.updatePassword(current_user.id, form.password.data):
            flash('Congratulations, you have successfully updated your password!')
            return redirect(url_for('users.profile'))
    return render_template('updatePassword.html', title='Update Password', form=form, seller_status=seller_status)

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
    seller_status = User.sellerStatus(current_user.id)
    curr_balance = User.get_balance(current_user.id)
    curr_balance = round(curr_balance, 2)
    form = BalanceForm()
    if form.validate_on_submit():
        if form.withdraw.data > float(curr_balance):
            flash('You cannot withdraw more than your current balance')
            return redirect(url_for('users.updateBalance'))
        else:
            new_balance = float(curr_balance) - form.withdraw.data
            new_balance = float(new_balance) + form.deposit.data
            new_balance = round(new_balance, 2)
            User.update_balance(current_user.id, new_balance)
            return redirect(url_for('users.profile'))
    return render_template('balance.html', title='Balance', form=form, curr_balance=curr_balance, seller_status=seller_status)
        
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


global currentProduct
currentProduct = '37'
global currentSeller
currentSeller = '4'

@bp.route('/userReviews/<int:user_id>')
def userReviews(user_id):
    seller_status = 0
    if current_user.is_authenticated:
        seller_status = User.sellerStatus(current_user.id)
    # get all product reviews user has made:
    productReviews = userProductReview.get(current_user.id) 
    # get all seller reviews user has made:
    sellerReviews = userSellerReview.get(current_user.id) 
    # render the page by adding information to the index.html file
    return render_template('userReviews.html',
                           userProductReviews=productReviews, userSellerReviews=sellerReviews, seller_status=seller_status)

    
@bp.route('/sellerReviews/<int:sel_id>')
def sellerReviews(sel_id):
    seller_status = 0
    if current_user.is_authenticated:
        seller_status = User.sellerStatus(current_user.id)
    # get all reviews for given seller: 
    reviews = sellerReview.get(sel_id) 
    total = len(reviews)
    if total == 0:
        average_rating = 0
    else:
        print(total)
        count = 0
        for review in reviews:
            count += review.num_stars
        average_rating = count / total
    # render the page by adding information to the index.html file
    return render_template('sellerSummaryReviews.html',
                           total=total, average_rating=average_rating, sellerReviews=reviews, seller_status=seller_status)
  
    
@bp.route('/productReviews/<int:sel_id>/<int:prod_id>')
def productReviews(sel_id, prod_id):
    seller_status = 0
    if current_user.is_authenticated:
        seller_status = User.sellerStatus(current_user.id)
    # get all reviews for given seller:
    reviews = productReview.get(prod_id, sel_id) 
    total = len(reviews)
    if total == 0:
        average_rating = 0
    else:
        print(total)
        count = 0
        for review in reviews:
            count += review.num_stars
        average_rating = count / total
    # render the page by adding information to the index.html file
    return render_template('productSummaryReviews.html',
                           total = total, average_rating=average_rating, productReviews=reviews, seller_status=seller_status)

class ReviewForm(FlaskForm):
    numStars= StringField(_l('Number of Stars'), validators=[DataRequired()])
    description = StringField(_l('Review'), validators=[DataRequired()])
    image1 = StringField(_l('Image 1 URL (optional)'))
    image2 = StringField(_l('Image 2 URL (optional)'))
    image3 = StringField(_l('Image 3 URL (optional)'))
    submit = SubmitField(_l('Submit'))


"""
Edit seller review 
parameters: id is seller_id
"""
@bp.route('/editSellerReview/<int:id>', methods=['GET', 'POST'])
def editSellerReview(id):
    seller_status = User.sellerStatus(current_user.id)
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userSellerReview.update_seller_review(current_user.id, id, form.numStars.data, str(date), form.description.data, '0', form.image1.data, form.image2.data, form.image3.data) 
        return redirect(url_for('users.userReviews', user_id=current_user.id))
    # render the page by adding information to the index.html file
    return render_template('editReview.html', title='Edit Review', form=form, seller_status=seller_status)

"""
Edit product review 
"""
@bp.route('/editProductReview/<int:prod_id>/<int:sel_id>', methods=['GET', 'POST'])
def editProductReview(prod_id, sel_id):
    seller_status = User.sellerStatus(current_user.id)
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userProductReview.update_product_review(current_user.id, prod_id, sel_id, form.numStars.data, str(date), form.description.data, '0', form.image1.data, form.image2.data, form.image3.data) 
        return redirect(url_for('users.userReviews', user_id=current_user.id))
    # render the page by adding information to the index.html file
    return render_template('editReview.html', title='Edit Review', form=form, seller_status=seller_status)

"""
Delete product review 
"""
@bp.route('/deleteProductReview/<int:prod_id>/<int:sel_id>', methods=['GET', 'POST'])
def deleteProductReview(prod_id, sel_id):
    userProductReview.delete_product_review(current_user.id, prod_id, sel_id) 
    return redirect(url_for('users.userReviews', user_id=current_user.id))

"""
Delete seller review 
parameters: id is seller_id
"""
@bp.route('/deleteSellerReview/<int:id>', methods=['GET', 'POST'])
def deleteSellerReview(id):
    userSellerReview.delete_seller_review(current_user.id, id) 
    return redirect(url_for('users.userReviews', user_id=current_user.id))

#Delete product review with specified id
@bp.route('/submitProductReview/<int:sel_id>/<int:prod_id>', methods=['GET', 'POST'])
def submitProductReview(sel_id, prod_id):
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userProductReview.submit_product_review(current_user.id, prod_id, sel_id, form.numStars.data, str(date), form.description.data, '0', form.image1.data, form.image2.data, form.image3.data) 
        return redirect(url_for('users.login'))
    return render_template('submitReview.html', title='Submit Review', form=form)

#Delete seller review with specified id
@bp.route('/submitSellerReview/<int:sel_id>', methods=['GET', 'POST'])
def submitSellerReview(sel_id):
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userSellerReview.submit_seller_review(current_user.id, sel_id, form.numStars.data, str(date), form.description.data, '0', form.image1.data, form.image2.data, form.image3.data) 
        return redirect(url_for('users.login'))
    return render_template('submitReview.html', title='Submit Review', form=form)


"""
Upvote product review 
"""
@bp.route('/upvoteProductReview/<int:buyer_id>/<int:prod_id>/<int:sel_id>/<int:upvotes>', methods=['GET', 'POST'])
def upvoteProductReview(buyer_id, prod_id, sel_id, upvotes):
    user_id = buyer_id 
    product_id = prod_id
    seller_id = sel_id
    upvotes = upvotes
    userProductReview.upvote_product_review(user_id, product_id, seller_id, upvotes)
    reviews = productReview.get(product_id, seller_id) 
    total = len(reviews)
    if total == 0:
        average_rating = 0
    else:
        print(total)
        count = 0
        for review in reviews:
            count += review.num_stars
        average_rating = count / total
    return render_template('productSummaryReviews.html',
                           total=total, average_rating=average_rating, productReviews=reviews)


"""
Upvote seller review 
"""
@bp.route('/upvoteSellerReview/<int:buyer_id>/<int:sel_id>/<int:upvotes>', methods=['GET', 'POST'])
def upvoteSellerReview(buyer_id, sel_id, upvotes):
    user_id = buyer_id
    seller_id = sel_id
    upvotes = upvotes
    userSellerReview.upvote_seller_review(user_id, seller_id, upvotes)
    reviews = sellerReview.get(seller_id)  
    total = len(reviews)
    if total == 0:
        average_rating = 0
    else:
        print(total)
        count = 0
        for review in reviews:
            count += review.num_stars
        average_rating = count / total
    return render_template('sellerSummaryReviews.html',
                           total=total, average_rating=average_rating, sellerReviews=reviews)
