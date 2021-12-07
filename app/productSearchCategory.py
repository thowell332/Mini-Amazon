from flask import render_template, request, Blueprint
from flask_paginate import Pagination, get_page_parameter

from .models.product import Product

bp = Blueprint('productSearchCategory', __name__)
per_page = 10

# Method to search for a product based on a category.
# @param input- the product category to be searched for.
# @return- a page with all products fitting this category.
@bp.route('/productSearchCategory<input>')
def product(input):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    product = Product.get_products_based_on_category(input) ##change "Laptop" to @param input
    pagination = Pagination(page=page, per_page=per_page, total=len(product), search=search, record_name='products')
    return render_template('productSearch.html', product=product[start: start + per_page], pagination=pagination)

# Method to redirect the user to the category select page.
# @return- the category select page.
@bp.route('/productViewCategories')
def productViewCategories():
    return render_template('productViewCategories.html')