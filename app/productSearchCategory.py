from flask import render_template

from .models.product import Product

from flask import Blueprint
bp = Blueprint('productSearchCategory', __name__)

@bp.route('/productSearchCategory')
def product():
    product = Product.get_products_based_on_category("Laptops") ##change "Laptop" to @param input
    print(product)
    return render_template('productSearch.html', product=product)
