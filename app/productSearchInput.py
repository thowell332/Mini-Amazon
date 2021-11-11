from flask import render_template

from .models.product import Product

from flask import Blueprint
bp = Blueprint('productSearchInput', __name__)

@bp.route('/productSearchInput')
def product():
    product = Product.get_products_based_on_search_criteria("test") ##change "Laptop" to @param input
    print(product)
    return render_template('productSearch.html', product=product)
