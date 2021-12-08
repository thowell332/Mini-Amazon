from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from datetime import datetime

from .models.user import User
from .models.userReviews import userProductReview, userSellerReview
from .models.sellerReviews import sellerReviewSummary, sellerReview
from .models.productReviews import productReviewSummary, productReview

from flask import Blueprint
bp = Blueprint('users', __name__)

class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user_info = User.get(current_user.id)
    return render_template('account.html', title = 'Profile', user_info = user_info)

@bp.route('/updateprofile', methods=['GET', 'POST'])
def updateProfile():
    user_info = User.get(current_user.id)
    form = RegistrationForm()

class BalanceForm(FlaskForm):
    withdraw = FloatField(_l('How much do you want to withdraw'))
    deposit = FloatField(_l('How much do you want to deposit'))
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

global currentUser 
currentUser = current_user.id
global currentProduct
currentProduct = '37'
global currentSeller
currentSeller = '4'

@bp.route('/userReviews/<int:user_id>')
def userReviews(user_id):
    # get all product reviews user has made:
    productReviews = userProductReview.get(currentUser) 
    # get all seller reviews user has made:
    sellerReviews = userSellerReview.get(currentUser) 
    # render the page by adding information to the index.html file
    return render_template('userReviews.html',
                           userProductReviews=productReviews, userSellerReviews=sellerReviews)


@bp.route('/sellerReviews/<int:sel_id>')
def sellerReviews(sel_id):
    # get all reviews for given seller:
    summary = sellerReviewSummary.get(sel_id) 
    reviews = sellerReview.get(sel_id) 
    # render the page by adding information to the index.html file
    return render_template('sellerSummaryReviews.html',
                           sellerReviewSummary=summary, sellerReviews=reviews)
  
   
@bp.route('/productReviews/<int:sel_id>/<int:prod_id>')
def productReviews(sel_id, prod_id):
    # get all reviews for given seller:
    summary = productReviewSummary.get(prod_id, sel_id) 
    reviews = productReview.get(prod_id, sel_id) 
    # render the page by adding information to the index.html file
    return render_template('productSummaryReviews.html',
                           productReviewSummary=summary, productReviews=reviews)

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
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userSellerReview.update_seller_review(currentUser, id, form.numStars.data, str(date), form.description.data, '0', form.image1.data, form.image2.data, form.image3.data) 
        return redirect(url_for('users.userReviews', user_id=currentUser))
    # render the page by adding information to the index.html file
    return render_template('editReview.html', title='Edit Review', form=form)

"""
Edit product review 
"""
@bp.route('/editProductReview/<int:prod_id>/<int:sel_id>', methods=['GET', 'POST'])
def editProductReview(prod_id, sel_id):
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userProductReview.update_product_review(currentUser, prod_id, sel_id, form.numStars.data, str(date), form.description.data, '0', form.image1.data, form.image2.data, form.image3.data) 
        return redirect(url_for('users.userReviews', user_id=currentUser))
    # render the page by adding information to the index.html file
    return render_template('editReview.html', title='Edit Review', form=form)

"""
Delete product review 
"""
@bp.route('/deleteProductReview/<int:prod_id>/<int:sel_id>', methods=['GET', 'POST'])
def deleteProductReview(prod_id, sel_id):
    userProductReview.delete_product_review(currentUser, prod_id, sel_id) 
    return redirect(url_for('users.userReviews', user_id=currentUser))

"""
Delete seller review 
parameters: id is seller_id
"""
@bp.route('/deleteSellerReview/<int:id>', methods=['GET', 'POST'])
def deleteSellerReview(id):
    userSellerReview.delete_seller_review(currentUser, id) #REMOVE HARD CODE
    return redirect(url_for('users.userReviews', user_id=currentUser))

#Delete product review with specified id
@bp.route('/submitProductReview/<int:sel_id>/<int:prod_id>', methods=['GET', 'POST'])
def submitProductReview(sel_id, prod_id):
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userProductReview.submit_product_review(currentUser, prod_id, sel_id, form.numStars.data, str(date), form.description.data, '0', form.image1.data, form.image2.data, form.image3.data) 
        return redirect(url_for('users.login'))
    return render_template('submitReview.html', title='Submit Review', form=form)

#Delete seller review with specified id
@bp.route('/submitSellerReview/<int:sel_id>', methods=['GET', 'POST'])
def submitSellerReview(sel_id):
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userSellerReview.submit_seller_review(currentUser, sel_id, form.numStars.data, str(date), form.description.data, '0', form.image1.data, form.image2.data, form.image3.data) 
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
    summary = productReviewSummary.get(product_id, seller_id)
    reviews = productReview.get(product_id, seller_id) 
    return render_template('productSummaryReviews.html',
                           productReviewSummary=summary, productReviews=reviews)


"""
Upvote seller review 
"""
@bp.route('/upvoteSellerReview/<int:buyer_id>/<int:sel_id>/<int:upvotes>', methods=['GET', 'POST'])
def upvoteSellerReview(buyer_id, sel_id, upvotes):
    user_id = buyer_id
    seller_id = sel_id
    upvotes = upvotes
    userSellerReview.upvote_seller_review(user_id, seller_id, upvotes)
    summary = sellerReviewSummary.get(seller_id) 
    reviews = sellerReview.get(seller_id) 
    return render_template('sellerSummaryReviews.html',
                           sellerReviewSummary=summary, sellerReviews=reviews)