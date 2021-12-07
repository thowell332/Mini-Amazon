from flask import render_template, redirect, url_for, flash, request, current_app as app
from werkzeug.datastructures import MultiDict
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.core import DateField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional
from flask_babel import _, lazy_gettext as _l

from .models.orderFulfillment import ItemFulfillment, OrderFulfillment, OrderHistory
from .models.product import Product

from flask import Blueprint
bp = Blueprint('orderFulfillments', __name__)

@bp.route('/orderFulfillments')
def orderFulfillments():
    # get order history
    orderHistory = OrderHistory.get('2') # CHANGE '2' TO USER ID
    # render the page by adding information to the index.html file
    return render_template('orderFulfillments.html', orderHistory=orderHistory)

@bp.route('/orderFulfillmentDetails/<int:purchase_id>', methods=['GET', 'POST'])
def orderFulfillmentDetails(purchase_id):
    purchase = OrderHistory.get_purchase(purchase_id)
    fulfillment = OrderFulfillment.get_order_fulfillment(purchase_id)
    # render the page by adding information to the index.html file
    return render_template('orderFulfillmentDetails.html', purchase=purchase, fulfillment=fulfillment)

class EditOrderForm(FlaskForm):
    item = SelectField(_l('Item ID'), coerce=int, validators=[DataRequired()])
    status = SelectField('Status', coerce=int, validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

@bp.route('/orderFulfillmentDetails/<int:purchase_id>/<int:product_id>', methods=['GET', 'POST'])
def editOrderFulfillment(purchase_id, product_id):
    purchase = OrderHistory.get_purchase(purchase_id)
    product = Product.get(product_id)
    # get item fulfillment statuses
    itemFulfillment = ItemFulfillment.get_item_fulfillment(purchase_id, product_id)
    itemList = [item.item_id for item in itemFulfillment]
    # create edit fulfillment form
    form = EditOrderForm()
    form.item.choices = [(-1, 'All Items')] + [(id, id) for id in itemList]
    form.status.choices = [(1, 'ORDERED'), (2, 'SHIPPED'), (3, 'DELIVERED')]
    if form.validate_on_submit():
        ItemFulfillment.update_status(purchase_id, product_id, form.item.data, form.status.data - 1)
        flash('Item fulfillment(s) has been updated')
        itemFulfillment = ItemFulfillment.get_item_fulfillment(purchase_id, product_id)
    # render the page by adding information to the index.html file
    return render_template('editOrderFulfillment.html', purchase=purchase, product=product, form=form, itemFulfillment=itemFulfillment)

