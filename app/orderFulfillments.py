from flask import render_template, redirect, url_for, flash, request, current_app as app
from werkzeug.datastructures import MultiDict
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.core import DateField, DecimalField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Optional
from flask_babel import _, lazy_gettext as _l

from .models.orderFulfillment import OrderHistory

from flask import Blueprint
bp = Blueprint('orderFulfillments', __name__)

@bp.route('/orderFulfillments')
def inventory():
    # get order history
    orderHistory = OrderHistory.get('2') # CHANGE '2' TO USER ID
    # render the page by adding information to the index.html file
    return render_template('orderFulfillments.html', orderHistory=orderHistory)

class EditOrderForm(FlaskForm):
    orderID = IntegerField(_l('Order ID'), validators=[Optional()])
    buyerName = StringField(_l('Buyer Name'), validators=[Optional()])
    buyerAddress = StringField(_l('Buyer Address'), validators=[Optional()])
    quantity = IntegerField(_l('Item Quantity'), validators=[Optional()])
    date = DateField(_l('Date'), validators=[Optional()])
    status = StringField('Status', validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

@bp.route('/orderFulfillmentDetails/<int:purchase_id>', methods=['GET', 'POST'])
def orderFulfillmentDetails(purchase_id):
    purchase = OrderHistory.get_order_fulfillment(purchase_id)
    form = EditOrderForm()
    if form.validate_on_submit():
        flash('Product listing has been updated')
        return redirect(url_for('inventories.inventory'))
    # render the page by adding information to the index.html file
    return render_template('editOrderFulfillment.html', title='View/Update Order Details', form=form, purchase=purchase)

