from flask import render_template, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_babel import _, lazy_gettext as _l

from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('cart', __name__)

class CartForm(FlaskForm):
    submit = SubmitField(_l('Purchase Cart'))


@bp.route('/cart', methods=['GET', 'POST'])
def cart():

    # TODO: Uncomment once functionality is there for logged in users.
    # if current_user.is_authenticated:
    #     return redirect(url_for('index.index'))
    # else:
    #     cart = Cart.get_by_buyer_id(current_user.id)

    # Test data for now.
    cart = Cart.get_cart_for_buyer_id(1)
    form = CartForm()

    # TODO: Show items that were out of stock.
    if form.validate_on_submit():
        Cart.purchase_cart_for_buyer_id(1)
        

    return render_template('cart.html', items=cart, form=form)
