from flask import render_template, redirect, url_for, flash, request
from flask_paginate import Pagination, get_page_parameter
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_babel import _, lazy_gettext as _l
from flask_login import current_user

from .models.purchase import Purchase, PurchaseSummary, PurchaseEntry

from flask import Blueprint
bp = Blueprint('purchases', __name__)

@bp.route('/purchases', methods=['GET', 'POST'])
def purchases():

    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    start = (page - 1) * per_page

    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    past_purchases = Purchase._get_purchases(current_user.id)
    print(past_purchases)
        
    pagination = Pagination(page=page, per_page=per_page, total=len(past_purchases), search=search, record_name='products')
    return render_template('purchases.html', purchases=past_purchases[start: start + per_page], pagination=pagination)

@bp.route('/individual-purchase<purchase_id>', methods=['GET', 'POST'])
def individual_purchase(purchase_id):

    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    purchase_entries = Purchase._get_individual_purchase(current_user.id, purchase_id)
    total_price_paid = Purchase._get_total_purchase_cost(current_user.id, purchase_id)
    total_price_paid = ('%.2f'%total_price_paid)

    return render_template('individualPurchase.html', purchase_id=purchase_id, purchase_entries=purchase_entries, total_price_paid=total_price_paid)