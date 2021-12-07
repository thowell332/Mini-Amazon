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
    cart = Cart.get_cart(80)
    total_cart_cost = Cart.get_total_cart_cost(80)

    # Initialize variables used for error handling.
    
    if 'type' in request.form:

        redirect_page = True

        if request.form['type'] == 'Delete Items':
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

                # Check to make sure that the new quantitty was specified.
                if quantity_to_move == '':
                    flash('You did not specify all quantities to move. Please do so!')
                    redirect_page = False
                    break

                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1], item_info[2], quantity_to_move])

            Cart.move_to_saved(80, formatted_items)

        elif request.form['type'] == 'Update Quantities':
            update_quantities = True

            items_to_update = request.form.getlist('update_quantity')
            formatted_items = []
            for item in items_to_update:
                print(item)
                new_quantity = request.form.get(item)
                
                # Check to make sure that the new quantitty was specified.
                if new_quantity == '':
                    flash('You did not specify all quantities to update. Please do so!')
                    redirect_page = False
                    break
                else:
                    item_info = item.split(',')
                    formatted_items.append([item_info[0], item_info[1], new_quantity])

            if update_quantities:
                Cart.update_cart_quantity(80, formatted_items)
        
        elif request.form['type'] == 'Purchase Cart':
            purchase_information = Cart.purchase_cart(80)
            result = purchase_information[0]

            # If the purchase failed because of an insufficient balance, show that.
            if result == "Balance Error":
                redirect_page = False
                current_balance = purchase_information[1]
                flash('Purchase failed due to insufficient funds. Your current balance is $' + str(current_balance) + '.')

            # If the purchase failed because an item is out of stock, show that.
            elif result == "Inventory Error":
                redirect_page = False
                out_of_stock = purchase_information[1]
                flash('The following item purchases are invalid:')
                for entry in out_of_stock:
                    cart_info = entry[0]
                    quantity_available = entry[1]
                    flash('You tried to purchase ' + str(cart_info.quantity) + ' of ' + cart_info.product_name + ' from ' + cart_info.seller_name + '. Only ' + str(quantity_available) + ' are in stock.')

        # Reload page to show updated data.
        if redirect_page:
            return redirect(url_for('cart.cart'))

        
    return render_template('cart.html', cart=cart, total_cost=total_cart_cost)

@bp.route('/saved-for-later', methods=['GET', 'POST'])
def saved_for_later():

    # TODO: Uncomment once functionality is there for logged in users.
    # if current_user.is_authenticated:
    #     return redirect(url_for('index.index'))
    # else:
    #     cart = Cart.get_by_buyer_id(current_user.id)

    # Test data for now.
    saved_for_later = Cart.get_saved(80)

    if 'type' in request.form:

        redirect_page = True

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

                # Check to make sure that the new quantitty was specified.
                if quantity_to_move == '':
                    flash('You did not specify all quantities to move. Please do so!')
                    redirect_page = False
                    break

                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1], item_info[2], quantity_to_move])

            Cart.move_to_cart(80, formatted_items)

        elif request.form['type'] == 'Update Quantities':
            items_to_update = request.form.getlist('update_quantity')
            formatted_items = []
            for item in items_to_update:
                new_quantity = request.form.get(item)

                # Check to make sure that the new quantitty was specified.
                if new_quantity == '':
                    flash('You did not specify all quantities to update. Please do so!')
                    redirect_page = False
                    break

                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1], new_quantity])

            Cart.update_saved_quantity(80, formatted_items)

        # Reload page to show updated data.
        if redirect_page:
            return redirect(url_for('cart.saved_for_later')) 
        
    return render_template('savedForLater.html', saved_for_later=saved_for_later)
