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
    cart = Cart.get_cart_for_buyer_id(98)

    immediate_cart = []
    saved_for_later_cart = []

    for cart_entry in cart:
        if cart_entry.saved_for_later:
            saved_for_later_cart.append(cart_entry)
        else:
            immediate_cart.append(cart_entry)

    print('here')
    print(immediate_cart)
    print(saved_for_later_cart)

    form = CartForm()

    # TODO: Show items that were out of stock.
    if form.validate_on_submit():
        print('called')
        # Cart.purchase_cart_for_buyer_id(38)
        
    return render_template('cart.html', immediate_cart=immediate_cart, saved_for_later_cart=saved_for_later_cart, purchase_form=form)
