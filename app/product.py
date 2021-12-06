from flask import render_template

from .models.product import Product

from flask import Blueprint
bp = Blueprint('product', __name__)

@bp.route('/product<input>')
def product(input):
    product = Product.get_product_display_page(input) ##replace 1 with @param id
    print(product)
    return render_template('product.html', product=product)
