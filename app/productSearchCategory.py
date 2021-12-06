from flask import render_template, request
from flask_paginate import Pagination, get_page_parameter

from .models.product import Product

from flask import Blueprint
bp = Blueprint('productSearchCategory', __name__)

per_page = 10

@bp.route('/productSearchCategory')
def product():
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    product = Product.get_products_based_on_category("Laptops") ##change "Laptop" to @param input
    pagination = Pagination(page=page, per_page=per_page, total=len(product), search=search, record_name='products')
    return render_template('productSearch.html', product=product[start: start + per_page], pagination=pagination)
