from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.core import IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l

from .models.userReviews import userProductReview, userSellerReview

from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('inventory', __name__)

@bp.route('/inventory')
def inventory():
    # get product inventory for given seller
    inventoryList = Inventory.get('2') #CHANGE '2' TO SELECTED PRODUCT ID
    # render the page by adding information to the index.html file
    return render_template('inventory.html',
                           inventory=inventoryList)

class EditInventoryForm(FlaskForm):
    price= StringField(_l('Price'), validators=[DataRequired()])
    quantity = IntegerField(_l('Quantity'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

@bp.route('/editInventory', methods=['GET', 'POST'])
def editInventory():
    form = EditInventoryForm()
    if form.validate_on_submit():
        Inventory.update_product_listing('5', '1', form.price, form.quantity)
        flash('Product listing has been updated')
        return redirect(url_for('users.inventory'))
    # render the page by adding information to the index.html file
    return render_template('editInventory.html', title='Edit Product Listing', form=form)

@bp.route('/deleteInventory', methods=['GET', 'POST'])
def deleteInventory():
    form = EditInventoryForm()
    if form.validate_on_submit():
        print("hi")
        userProductReview.update_product_review('5', '1', form.numStars.data, '10/20/21 0:00', form.description.data)
        userSellerReview.update_seller_review('5', '2', form.numStars.data, '10/20/21 0:00', form.description.data)
        flash('Review has been updated')
        return redirect(url_for('users.userReviews'))
    # render the page by adding information to the index.html file
    return render_template('editReview.html', title='Edit Review', form=form) 
