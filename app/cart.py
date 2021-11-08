from flask import render_template

from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('cart', __name__)

@bp.route('/cart')
def cart():
    cart = Cart.get_by_buyer_id(4)
    return render_template('cart.html', cart_items=cart)
