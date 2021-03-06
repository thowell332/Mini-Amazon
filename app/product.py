from flask import render_template, Blueprint, request, redirect, url_for, flash
from flask_paginate import Pagination, get_page_parameter
from flask_wtf import FlaskForm
from wtforms import StringField
from flask_babel import _, lazy_gettext as _l

from .models.product import Product
from .models.cart import Cart
from .models.user import User
from flask_login import current_user

bp = Blueprint('product', __name__)
per_page = 10

# Method to search for a product based on a product id.
# @param input- the product_id being searched for.
# @param sort- the sorting type of the returned products (if any).
# @return- the page displaying the product(s) with product_id = @param input.
@bp.route('/product<input>/<sort>', methods=['GET', 'POST'])
def product(input, sort):
    # get seller status
    seller_status = 0
    if current_user.is_authenticated:
        seller_status = User.sellerStatus(current_user.id)
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    
    # Check to see if the user wants to add items to cart or save them for later.
    for key in request.form.keys():
        # The user wants to add to his cart.
        if 'add' in key or 'save' in key:
            if not current_user.is_authenticated:
                flash('')
                flash('You must login before purchasing any items.')
                break
            
            else:
                info = key.split(',')
                product_id = info[1]
                seller_id = info[2]
                quantity_key = 'quantity,' + product_id + ',' + seller_id
                quantity_to_move = request.form.get(quantity_key)

                # Check to make sure that the new quantitty was specified.
                if quantity_to_move == '':
                    flash('You did not specify the quantity to move. Please do so!')
                    break

                saved_for_later = "TRUE" if 'save' in key else "FALSE"
                
                Cart.add_values_into_cart(current_user.id, product_id, seller_id, quantity_to_move, saved_for_later)
                if saved_for_later=="TRUE":
                    flash('Successfully added items to saved for later!')
                else:
                    flash('Successfully added items to cart!')
                break
    
    ## determine how to sort product
    if sort == "quantity-ordered":
        product = Product.get_product_display_page(input, "COUNT(si.item_id)")
    elif sort == "price-ordered":
        product = Product.get_product_display_page(input, "sp.price")
    else:
        product = Product.get_product_display_page(input, "sp.seller_id")
    ## if no products being sold, tell user
    if (len(product) == 0):
        return render_template('noProductsBeingSold.html', seller_status=seller_status)
    ## display products being sold
    else:
        productid = product[0].product_id
        pagination = Pagination(page=page, per_page=per_page, total=len(product), record_name='products')
        return render_template('product.html', product=product[start: start + per_page], productid=productid, pagination=pagination, seller_status=seller_status)

@bp.route('/productOwner')
def productOwner():
    # redirect to login if not authenticated
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    
    # redirect to homepage if not seller
    seller_status = User.sellerStatus(current_user.id)
    if seller_status != 1:
        return redirect(url_for('index.index'))
    
    # set up pagination
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * per_page
    productList = Product.get_seller_products(current_user.id)
    pagination = Pagination(page=page, per_page=per_page, total=len(productList), search=search, record_name='products')
    
    # render the page by adding information to the index.html file
    return render_template('productOwner.html', productList=productList[start: start + per_page], pagination=pagination, seller_status=1)

