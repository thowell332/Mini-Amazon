from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_babel import _, lazy_gettext as _l

from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('cart', __name__)

@bp.route('/cart', methods=['GET', 'POST'])
def cart():

    # TODO: Uncomment once functionality is there for logged in users.
    # if current_user.is_authenticated:
    #     return redirect(url_for('index.index'))
    # else:
    #     cart = Cart.get_by_buyer_id(current_user.id)

    # Test data for now.
    cart = Cart.get_cart_for_buyer_id(80)
    if 'type' in request.form:
        if request.form['type'] == 'Delete Items':
            print('Called Delete')
            items_to_delete = request.form.getlist('delete_from_cart')
            formatted_items = []
            for item in items_to_delete:
                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1]])

            Cart.delete_from_cart(80, formatted_items)            

        elif request.form['type'] == 'Move Items to Saved':
            items_to_move = request.form.getlist('move_to_saved')
            formatted_items = []
            for item in items_to_move:
                quantity_to_move = request.form.get(item)
                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1], item_info[2], quantity_to_move])

            Cart.move_to_saved(80, formatted_items)

        elif request.form['type'] == 'Update Quantities':
            items_to_update = request.form.getlist('update_quantity')
            formatted_items = []
            for item in items_to_update:
                new_quantity = request.form.get(item)
                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1], new_quantity])

            Cart.update_cart_quantity(80, formatted_items)

        # Reload page to show updated data.
        return redirect(url_for('cart.cart'))

        
    return render_template('cart.html', cart=cart)

@bp.route('/saved-for-later', methods=['GET', 'POST'])
def saved_for_later():

    # TODO: Uncomment once functionality is there for logged in users.
    # if current_user.is_authenticated:
    #     return redirect(url_for('index.index'))
    # else:
    #     cart = Cart.get_by_buyer_id(current_user.id)

    # Test data for now.
    saved_for_later = Cart.get_saved_for_buyer_id(80)

    if 'type' in request.form:
        if request.form['type'] == 'Delete Items':
            items_to_delete = request.form.getlist('delete_from_saved')
            formatted_items = []
            for item in items_to_delete:
                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1]])

            Cart.delete_from_saved(80, formatted_items)            

        elif request.form['type'] == 'Move Items to Cart':
            items_to_move = request.form.getlist('move_to_cart')
            formatted_items = []
            for item in items_to_move:
                quantity_to_move = request.form.get(item)
                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1], item_info[2], quantity_to_move])

            Cart.move_to_cart(80, formatted_items)

        elif request.form['type'] == 'Update Quantities':
            items_to_update = request.form.getlist('update_quantity')
            formatted_items = []
            for item in items_to_update:
                new_quantity = request.form.get(item)
                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1], new_quantity])

            Cart.update_saved_quantity(formatted_items, 80)

        # Reload page to show updated data.
        return redirect(url_for('cart.saved_for_later')) 
        
    return render_template('savedForLater.html', saved_for_later=saved_for_later)
