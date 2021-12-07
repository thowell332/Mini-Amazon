from flask import render_template, Blueprint, request
from flask_paginate import Pagination, get_page_parameter
from flask_wtf import FlaskForm
from wtforms import StringField
from flask_babel import _, lazy_gettext as _l

from .models.product import Product

bp = Blueprint('product', __name__)
per_page = 10

# Method to search for a product based on a product id.
# @param input- the product_id being searched for.
# @param sort- the sorting type of the returned products (if any).
# @return- the page displaying the product(s) with product_id = @param input.
@bp.route('/product<input>/<sort>')
def product(input, sort):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    ##determine how to sort product
    if sort == "quantity-ordered":
        product = Product.get_product_display_page(input, 'COUNT(si.item_id)')
    elif sort == "price-ordered":
        product = Product.get_product_display_page(input, "sp.price")
    else:
        product = Product.get_product_display_page(input, 'sp.seller_id')
    ##if no products being sold, tell user
    if (len(product) == 0):
        return render_template('noProductsBeingSold.html')
    ##display products being sold
    else:
        productid = product[0].product_id
        pagination = Pagination(page=page, per_page=per_page, total=len(product), search=search, record_name='products')
        return render_template('product.html', product=product[start: start + per_page], productid=productid, pagination=pagination)
