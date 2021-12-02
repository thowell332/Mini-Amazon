from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
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


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
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
                         form.lastname.data):
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
currentUser = '5'
currentProduct = '1'
@bp.route('/userReviews')
def userReviews():
    # get all product reviews user has made:
    productReviews = userProductReview.get(currentUser) #CHANGE '5' TO CURRENT USER ID
    sellerReviews = userSellerReview.get(currentUser) #CHANGE '5' TO CURRENT USER ID
    print(current_user.get_id())
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
    summary = productReviewSummary.get(currentProduct) #CHANGE '2' TO SELECTED PRODUCT ID
    reviews = productReview.get(currentProduct) #CHANGE '2' TO SELECTED PRODUCT ID
    # render the page by adding information to the index.html file
    return render_template('productSummaryReviews.html',
                           productReviewSummary=summary, productReviews=reviews)

class ReviewForm(FlaskForm):
    numStars= StringField(_l('Number of Stars'), validators=[DataRequired()])
    description = StringField(_l('Review'), validators=[DataRequired()])
    images = StringField(_l('Images'), validators=[DataRequired()])
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
        userSellerReview.update_seller_review(currentUser, id, form.numStars.data, str(date), form.description.data, form.images.data) #REMOVE HARD CODE
        flash('Review has been updated')
        return redirect(url_for('users.userReviews'))
    # render the page by adding information to the index.html file
    return render_template('editReview.html', title='Edit Review', form=form)

"""
Edit product review 
parameters: id is product_id
"""
@bp.route('/editProductReview/<int:id>', methods=['GET', 'POST'])
def editProductReview(id):
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userProductReview.update_product_review(currentUser, id, form.numStars.data, str(date), form.description.data, form.images.data) #REMOVE HARD CODE
        flash('Review has been updated')
        return redirect(url_for('users.userReviews'))
    # render the page by adding information to the index.html file
    return render_template('editReview.html', title='Edit Review', form=form)

"""
Delete product review 
parameters: id is product_id
"""
@bp.route('/deleteProductReview/<int:id>', methods=['GET', 'POST'])
def deleteProductReview(id):
    userProductReview.delete_product_review(currentUser, id) #REMOVE HARD CODE
    flash('Review has been deleted')
    return redirect(url_for('users.userReviews'))

"""
Delete seller review 
parameters: id is seller_id
"""
@bp.route('/deleteSellerReview/<int:id>', methods=['GET', 'POST'])
def deleteSellerReview(id):
    userSellerReview.delete_seller_review(currentUser, id) #REMOVE HARD CODE
    flash('Review has been deleted')
    return redirect(url_for('users.userReviews'))

#Delete product review with specified id
@bp.route('/submitProductReview', methods=['GET', 'POST'])
#IMPLEMENT GET ID
def submitProductReview():
    #<input type="hidden" name="product_id" value="{{product_review.num_stars}}" />
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userProductReview.submit_product_review(currentUser, '1', form.numStars.data, str(date), form.description.data, '0', form.images.data) #REMOVE HARD CODE FOR PRODUCT_ID
        flash('Product Review has been submitted')
        return redirect(url_for('users.login'))
    return render_template('submitReview.html', title='Submit Review', form=form)

#Delete seller review with specified id
@bp.route('/submitSellerReview', methods=['GET', 'POST'])
#IMPLEMENT GET ID
def submitSellerReview():
    #<input type="hidden" name="num_stars" value="{{product_review.num_stars}}" />
    form = ReviewForm()
    if form.validate_on_submit():
        date = datetime.now()
        userSellerReview.submit_seller_review(currentUser, '2', form.numStars.data, str(date), form.description.data, '0', form.images.data) #REMOVE HARD CODE FOR SELLER_ID
        flash('Seller Review has been submitted')
        return redirect(url_for('users.login'))
    return render_template('submitReview.html', title='Submit Review', form=form)


"""
Upvote product review 
"""
@bp.route('/upvoteProductReview/<int:id>/<int:upvotes>', methods=['GET', 'POST'])
def upvoteProductReview(id, upvotes):
    user_id = id 
    product_id = currentProduct #Change to current product id
    upvotes = upvotes
    print('User ID:', user_id) 
    print('Product ID:', product_id) 
    print('Upvotes:', upvotes) 
    userProductReview.upvote_product_review(user_id, product_id, upvotes)
    summary = productReviewSummary.get(currentProduct) #CHANGE '2' TO SELECTED PRODUCT ID
    reviews = productReview.get(currentProduct) #CHANGE '2' TO SELECTED PRODUCT ID
    return render_template('productSummaryReviews.html',
                           productReviewSummary=summary, productReviews=reviews)


"""
Upvote seller review 
"""
@bp.route('/upvoteSellerReview', methods=['GET', 'POST'])
def upvoteSellerReview():
    user_id = currentUser #Change to current user id
    args = flask.request.args
    seller_id = args.get("id")
    upvotes = args.get("upvotes")
    
    userReviews.upvote_seller_review(user_id, seller_id, upvotes)
    return render_template('sellerSummaryReviews.html',
                           sellerReviewSummary=summary, sellerReviews=reviews)