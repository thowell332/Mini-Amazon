from flask import render_template, request, Blueprint, redirect, url_for
from flask_paginate import Pagination, get_page_parameter

from .models.product import Product

bp = Blueprint('productSearchInput', __name__)
per_page = 10

@bp.route('/productSearchInputSearchCriteria', methods=['POST'])
def handle_search():
    search_criteria = request.form['search_criteria']
    return redirect(url_for('productSearchInput.product', input=search_criteria))

@bp.route('/productSearchInput<input>')
##change to @bp.route('/productSearchInput<input>')
##make the below function take in @param input
def product(input):
    if input == None:
        return render_template('index.html')
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    product = Product.get_products_based_on_search_criteria(input) ##change "Laptop" to @param input
    pagination = Pagination(page=page, per_page=per_page, total=len(product), search=search, record_name='products')
    return render_template('productSearch.html', product=product[start: start + per_page], pagination=pagination)
#
