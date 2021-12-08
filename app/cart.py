from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_babel import _, lazy_gettext as _l
from flask_login import current_user

from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('cart', __name__)

# Route to show a user's cart.
@bp.route('/cart', methods=['GET', 'POST'])
def cart():

    # Redirect if not logged in.
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    # Get cart and cost.
    cart = Cart.get_cart(current_user.id)
    total_cart_cost = Cart.get_total_cart_cost(current_user.id)
    total_cart_cost = ('%.2f'%total_cart_cost)
    
    # Respond to user input via buttons. 
    if 'type' in request.form:

        redirect_page = True

        if request.form['type'] == 'Delete Items':
            items_to_delete = request.form.getlist('delete_from_cart')
            formatted_items = []
            for item in items_to_delete:
                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1]])

            Cart.delete_from_cart(current_user.id, formatted_items)            

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

            Cart.move_to_saved(current_user.id, formatted_items)

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
                Cart.update_cart_quantity(current_user.id, formatted_items)
        
        elif request.form['type'] == 'Purchase Cart':
            purchase_information = Cart.purchase_cart(current_user.id)
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

# Route to show a user's saved for later section.
@bp.route('/saved-for-later', methods=['GET', 'POST'])
def saved_for_later():

    # Redirect if not logged in.
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    # Get items saved for later.

    saved_for_later = Cart.get_saved(current_user.id)

    # Respond to user feedback via buttons.
    if 'type' in request.form:

        redirect_page = True

        if request.form['type'] == 'Delete Items':
            items_to_delete = request.form.getlist('delete_from_saved')
            formatted_items = []
            for item in items_to_delete:
                item_info = item.split(',')
                formatted_items.append([item_info[0], item_info[1]])

            Cart.delete_from_saved(current_user.id, formatted_items)            

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

            Cart.move_to_cart(current_user.id, formatted_items)

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

            Cart.update_saved_quantity(current_user.id, formatted_items)

        # Reload page to show updated data.
        if redirect_page:
            return redirect(url_for('cart.saved_for_later')) 
        
    return render_template('savedForLater.html', saved_for_later=saved_for_later)
