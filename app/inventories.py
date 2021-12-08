from flask import render_template, redirect, url_for, flash, request, current_app as app
from werkzeug.datastructures import MultiDict
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.core import DecimalField, IntegerField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Optional
from flask_babel import _, lazy_gettext as _l

from .models.userReviews import userProductReview, userSellerReview

from .models.inventory import Inventory, InventoryListing

from flask import Blueprint
bp = Blueprint('inventories', __name__)

@bp.route('/inventory')
def inventory():
    # get product inventory for given seller
    inventoryList = Inventory.get('2') #CHANGE '5' TO USER ID
    # render the page by adding information to the index.html file
    return render_template('inventory.html', inventory=inventoryList)

class EditInventoryForm(FlaskForm):
    name = StringField(_l('Product Name'), validators=[Optional()])
    description = StringField(_l('Description'), validators=[Optional()])
    price = DecimalField(_l('Price'), validators=[InputRequired(), NumberRange(min=0, message='Price cannot be negative.')])
    quantity = IntegerField(_l('Quantity'), validators=[InputRequired(), NumberRange(min=0, message='Quantity cannot be negative.')])
    submit = SubmitField(_l('Submit'))

@bp.route('/editInventory/<int:product_id>', methods=['GET', 'POST'])
def editInventory(product_id):
    product = InventoryListing.get_product_listing('2', product_id) #CHANGE '5' TO USER ID
    form = EditInventoryForm()
    if form.validate_on_submit():
        InventoryListing.edit_product_listing('2', product_id, form.price.data, form.quantity.data - product.quantity) #CHANGE '5' TO USER ID
        flash('Product listing has been updated')
        return redirect(url_for('inventories.inventory'))
    # render the page by adding information to the index.html file
    return render_template('editInventory.html', title='Edit Product Listing', form=form, product=product)

class AddInventoryForm(FlaskForm):
    name = StringField(_l('Product Name'), validators=[DataRequired()])
    price = DecimalField(_l('Price'), validators=[InputRequired(), NumberRange(min=0, message='Price cannot be negative.')])
    quantity = IntegerField(_l('Quantity'), validators=[InputRequired(), NumberRange(min=0, message='Quantity cannot be negative.')])
    submit = SubmitField(_l('Submit'))

@bp.route('/addInventory', methods=['GET', 'POST'])
def addInventory():
    form = AddInventoryForm()
    if form.validate_on_submit():
        InventoryListing.add_product_listing('2', form) #CHANGE '5' TO USER ID
        flash('Product listing has been updated')
        return redirect(url_for('inventories.inventory'))
    # render the page by adding information to the index.html file
    return render_template('addInventory.html', title='Add Product Listing', form=form)

@bp.route('/deleteInventory/<int:product_id>', methods=['GET', 'POST'])
def deleteInventory(product_id):
    # execute deletion of inventory
    InventoryListing.delete_product_listing('2', product_id) #CHANGE '5' TO USER ID
    # render inventory page
    return redirect(url_for('inventories.inventory'))

