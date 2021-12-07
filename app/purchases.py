from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_babel import _, lazy_gettext as _l
from flask_login import current_user

from .models.purchase import Purchase, PurchaseSummary

from flask import Blueprint
bp = Blueprint('purchases', __name__)

@bp.route('/purchases')
def purchases():

    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    past_purchases = Purchase._get_purchases(current_user.id)
    for i in range(100):
        past_purchases.append(PurchaseSummary(i, i, i))
    print('past purchases')
    print(past_purchases)
    return render_template('purchases.html', purchases=past_purchases)