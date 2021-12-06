from flask import render_template, Blueprint, request
from flask_paginate import Pagination, get_page_parameter

from .models.product import Product

bp = Blueprint('product', __name__)
per_page = 10

@bp.route('/product<input>')
def product(input):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    product = Product.get_product_display_page(input)
    print(product)
    pagination = Pagination(page=page, per_page=per_page, total=len(product), search=search, record_name='products')
    return render_template('product.html', product=product[start: start + per_page], pagination=pagination)

@bp.route('/productpricesort<input>')
def product_price_sort(input):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    product = Product.get_product_display_page_price_ordered(input)
    pagination = Pagination(page=page, per_page=per_page, total=len(product), search=search, record_name='products')
    return render_template('product.html', product=product[start: start + per_page], pagination=pagination)

@bp.route('/productquantitysort<input>')
def product_quantity_sort(input):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    product = Product.get_product_display_page_quantity_ordered(input)
    pagination = Pagination(page=page, per_page=per_page, total=len(product), search=search, record_name='products')
    return render_template('product.html', product=product[start: start + per_page], pagination=pagination)
