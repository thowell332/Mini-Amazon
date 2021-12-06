from flask import render_template

from .models.product import Product

from flask import Blueprint
bp = Blueprint('product', __name__)

@bp.route('/product<input>')
def product(input):
    product = Product.get_product_display_page(input)
    return render_template('product.html', product=product)

@bp.route('/productpricesort<input>')
def product_price_sort(input):
    product = Product.get_product_display_page_price_ordered(input)
    return render_template('product.html', product=product)

@bp.route('/productquantitysort<input>')
def product_quantity_sort(input):
    product = Product.get_product_display_page_quantity_ordered(input)
    return render_template('product.html', product=product)
