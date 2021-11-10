from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l

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

@bp.route('/editSellerReview/<int:id>', methods=['GET', 'POST'])
def editSellerReview(id):
    form = EditReviewForm()
    if form.validate_on_submit():
        userSellerReview.update_seller_review('5', id, form.numStars.data, '10/20/21 0:00', form.description.data) #REMOVE HARD CODE
        flash('Review has been updated')
        return redirect(url_for('users.userReviews'))
    # render the page by adding information to the index.html file
    return render_template('editReview.html', title='Edit Review', form=form)

@bp.route('/editProductReview/<int:id>', methods=['GET', 'POST'])
def editProductReview(id):
    form = EditReviewForm()
    if form.validate_on_submit():
        userProductReview.update_product_review('5', id, form.numStars.data, '10/20/21 0:00', form.description.data) #REMOVE HARD CODE
        flash('Review has been updated')
        return redirect(url_for('users.userReviews'))
    # render the page by adding information to the index.html file
    return render_template('editReview.html', title='Edit Review', form=form)


@bp.route('/deleteProductReview/<int:id>', methods=['GET', 'POST'])
def deleteProductReview(id):
    userProductReview.delete_product_review('5', id) #REMOVE HARD CODE
    flash('Review has been deleted')
    return redirect(url_for('users.userReviews'))

@bp.route('/deleteSellerReview/<int:id>', methods=['GET', 'POST'])
def deleteSellerReview(id):
    userSellerReview.delete_seller_review('5', id) #REMOVE HARD CODE
    flash('Review has been deleted')
    return redirect(url_for('users.userReviews'))
