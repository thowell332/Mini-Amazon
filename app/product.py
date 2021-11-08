from flask import render_template

from .models.product import Product

from flask import Blueprint
bp = Blueprint('product', __name__)

@bp.route('/product')
def product():
    product = Product.get_product_display_page(1)
    print(product)
    return render_template('product.html', product=product)
