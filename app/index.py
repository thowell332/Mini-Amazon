from flask import render_template, request
from flask_login import current_user
import datetime
from flask_paginate import Pagination, get_page_parameter

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('index', __name__)

# Home route
@bp.route('/')
def index():

    # Set up pagination.
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    start = (page - 1) * per_page


    # Get all available products for sale.
    products = Product.get_all()

    # Render the page by adding information to the index.html file
    pagination = Pagination(page=page, per_page=per_page, total=len(products), record_name='products')
    return render_template('index.html', avail_products=products[start: start + per_page],pagination=pagination)
                           