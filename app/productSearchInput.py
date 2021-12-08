from flask import render_template, request, Blueprint, redirect, url_for
from flask_paginate import Pagination, get_page_parameter
from flask_login import current_user

from .models.product import Product
from .models.user import User

bp = Blueprint('productSearchInput', __name__)
per_page = 10

# Method to gather the user's search input and redirect the user to the results page.
# @return- the resulting product search page based on the search criteria.
@bp.route('/productSearchInputSearchCriteria', methods=['POST'])
def handle_search():
    
    search_criteria = request.form['search_criteria']
    return redirect(url_for('productSearchInput.product', input=search_criteria))

# Method to get and display all products based on a given search criteria.
# @param input- the search criteria.
# @return- the product search page containing all products based on that search criteria.
@bp.route('/productSearchInput<input>')
def product(input):
    # get seller status
    seller_status = 0
    if current_user.is_authenticated:
        seller_status = User.sellerStatus(current_user.id)
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    product = Product.get_products_based_on_search_criteria(input)
    pagination = Pagination(page=page, per_page=per_page, total=len(product), record_name='products')
    return render_template('productSearch.html', product=product[start: start + per_page], pagination=pagination, seller_status=seller_status)
#
