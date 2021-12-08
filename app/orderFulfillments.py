from flask import render_template, redirect, url_for, flash, request, current_app as app
from werkzeug.datastructures import MultiDict
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.core import DateField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional, InputRequired
from flask_babel import _, lazy_gettext as _l
from flask_paginate import Pagination, get_page_parameter

from .models.orderFulfillment import ItemFulfillment, OrderFulfillment, OrderHistory
from .models.product import Product

from flask import Blueprint
bp = Blueprint('orderFulfillments', __name__)
per_page = 10

@bp.route('/orderFulfillments', methods=['GET', 'POST'])
def orderFulfillments():
    # check if search criteria is applied
    search_field = None
    search_criteria = None
    if request.form:
        search_field = request.form['search_field']
        search_criteria = request.form['search_criteria']
        return redirect(url_for('orderFulfillments.orderFulfillmentSearch', search_field=search_field, search_criteria=search_criteria))
    # get order history
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    orderHistory = OrderHistory.get('2') # CHANGE '2' TO USER ID
    pagination = Pagination(page=page, per_page=per_page, total=len(orderHistory), search=search, record_name='orderHistory')
    # render the page by adding information to the index.html file
    return render_template('orderFulfillments.html', orderHistory=orderHistory[start: start + per_page], pagination=pagination)

@bp.route('/orderFulfillments;<search_field>;<search_criteria>', methods=['GET', 'POST'])
def orderFulfillmentSearch(search_field, search_criteria):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    orderHistory = OrderHistory.get_search_results('2', search_field, search_criteria) # CHANGE '2' TO USER ID
    pagination = Pagination(page=page, per_page=per_page, total=len(orderHistory), search=search, record_name='orderHistory')
    return render_template(
        'orderFulfillments.html',
        orderHistory=orderHistory[start: start + per_page], 
        pagination=pagination,
        search_field=search_field,
        search_criteria=search_criteria
    )

@bp.route('/orderFulfillmentDetails/<int:purchase_id>', methods=['GET', 'POST'])
def orderFulfillmentDetails(purchase_id):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    purchase = OrderHistory.get_purchase(purchase_id)
    fulfillment = OrderFulfillment.get_order_fulfillment(purchase_id)
    pagination = Pagination(page=page, per_page=per_page, total=len(fulfillment), search=search, record_name='fulfillment')
    # render the page by adding information to the index.html file
    return render_template(
        'orderFulfillmentDetails.html', 
        purchase=purchase, 
        fulfillment=fulfillment[start: start + per_page],
        pagination=pagination
    )

class EditOrderForm(FlaskForm):
    item = SelectField(_l('Item ID'), coerce=int, validators=[DataRequired()])
    status = SelectField('Status', coerce=int, validators=[InputRequired()])
    submit = SubmitField(_l('Submit'))

@bp.route('/orderFulfillmentDetails/<int:purchase_id>/<int:product_id>', methods=['GET', 'POST'])
def editOrderFulfillment(purchase_id, product_id):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    purchase = OrderHistory.get_purchase(purchase_id)
    product = Product.get(product_id)
    # get item fulfillment statuses
    itemFulfillment = ItemFulfillment.get_item_fulfillment(purchase_id, product_id)
    itemList = [item.item_id for item in itemFulfillment]
    pagination = Pagination(page=page, per_page=per_page, total=len(itemFulfillment), search=search, record_name='itemFulfillment')
    # create edit fulfillment form
    form = EditOrderForm()
    form.item.choices = [(-1, 'All Items')] + [(id, id) for id in itemList]
    form.status.choices = [(0, 'ORDERED'), (1, 'SHIPPED'), (2, 'DELIVERED')]
    if form.validate_on_submit():
        ItemFulfillment.update_status(purchase_id, product_id, form.item.data, form.status.data)
        flash('Item fulfillment(s) has been updated')
        itemFulfillment = ItemFulfillment.get_item_fulfillment(purchase_id, product_id)
    # render the page by adding information to the index.html file
    return render_template(
        'editOrderFulfillment.html',
        purchase=purchase,
        product=product,
        form=form,
        itemFulfillment=itemFulfillment[start: start + per_page],
        pagination=pagination
        )

