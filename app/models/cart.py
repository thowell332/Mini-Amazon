from flask import current_app as app
from datetime import datetime

class Cart:
    def __init__(self, product_id, product_name, product_image, seller_id, seller_first_name, seller_last_name, quantity, unit_price):
        self.product_id = product_id
        self.product_name = product_name
        self.product_image = product_image
        self.seller_id = seller_id
        self.seller_name = seller_first_name + ' ' + seller_last_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = self.unit_price * self.quantity

# METHODS USED TO QUERY DATA FROM THE CART DATABASE.

    # Gets all the items in the cart that are NOT saved for later.
    # @buyer_id is the owner of the cart.
    @staticmethod
    def get_cart_for_buyer_id(buyer_id):
        return Cart._get_info_for_buyer_id(buyer_id, "FALSE")
        
    # Gets all the items in the cart that ARE saved for later.
    # @buyer_id is the owner of the cart.
    @staticmethod
    def get_saved_for_buyer_id(buyer_id):
        return Cart._get_info_for_buyer_id(buyer_id, "TRUE")

    # Gets all the items in the cart that are either saved for later or not, depending on the parameter.
    # @saved_for_later is either "TRUE" or "FALSE", depending on whether we are interested in saved for later items or not, respectively.
    @staticmethod
    def _get_info_for_buyer_id(buyer_id, saved_for_later):
        
        # Execute a complex query to get all information needed to visualize the cart in the UI.
        # This requires joining sevaral relations.
        rows = app.db.execute(
"""
WITH
BasicCart(product_id, seller_id, quantity) AS (
    SELECT product_id, seller_id, quantity
    FROM Cart
    WHERE buyer_id = :buyer_id and saved_for_later = :saved_for_later
),

CartAddPrice(product_id, seller_id, quantity, unit_price) AS (
    SELECT BasicCart.product_id, BasicCart.seller_id, BasicCart.quantity, SellsProduct.price
    FROM BasicCart
    LEFT JOIN
    SellsProduct
    ON BasicCart.seller_id = SellsProduct.seller_id AND BasicCart.product_id = SellsProduct.product_id
),

CartAddProduct(product_id, product_name, product_image, seller_id, quantity, unit_price) AS (
    SELECT CartAddPrice.product_id, Product.name, Product.image, CartAddPrice.seller_id, CartAddPrice.quantity, CartAddPrice.unit_price
    FROM CartAddPrice
    LEFT JOIN
    Product
    ON CartAddPrice.product_id = Product.product_id
),

FullCart(product_id, product_name, product_image, seller_id, seller_first_name, seller_last_name, quantity, unit_price) AS (
    SELECT CartAddProduct.product_id, CartAddProduct.product_name, CartAddProduct.product_image, CartAddProduct.seller_id, Account.firstname, Account.lastname, CartAddProduct.quantity, CartAddProduct.unit_price
    FROM CartAddProduct
    LEFT JOIN
    Account
    ON CartAddProduct.seller_id = Account.account_id
)
Select * FROM FullCart
""",
buyer_id = buyer_id, saved_for_later = saved_for_later)

        # If no results came back, return an empty array.
        if not rows:  
            return []
        # Otherwise, format the information into Python objects.
        else:
            return [Cart(*row) for row in rows]

# METHODS USED TO DELETE ENTRIES FROM THE CART DATABASE.

    # Deletes an entry that is in the cart, meaning that it is NOT saved for later.
    # @entries_to_delete are arrays with product_id and seller_id combinations.
    # @buyer_id is the ID for the owner of the cart. 
    @staticmethod
    def delete_from_cart(buyer_id, entries_to_delete):
        for cart_entry in entries_to_delete:
            product_id = cart_entry[0]
            seller_id = cart_entry[1]
            Cart._delete_from_db(buyer_id, product_id, seller_id, "FALSE")                 

    # Deletes an entry that is saved, meaning that it IS saved for later.
    # @entries_to_delete are arrays with product_id and seller_id combinations.
    # @buyer_id is the ID for the owner of the cart. 
    @staticmethod
    def delete_from_saved(buyer_id, entries_to_delete):
        for cart_entry in entries_to_delete:
            product_id = cart_entry[0]
            seller_id = cart_entry[1]     
            Cart._delete_from_db(buyer_id, product_id, seller_id, "TRUE")                 

    # Private helper method to delete from the database.
    # @buyer_id is the owner of the cart.
    # @product_id is the ID for the product being removed.
    # @seller_id is the ID for the vendor selling the product to be removed.
    # @saved_for_later details whether or not the item is in the cart or saved table.
    @staticmethod
    def _delete_from_db(buyer_id, product_id, seller_id, saved_for_later):
        print('delete call')
        print(buyer_id)
        print(product_id)
        print(seller_id)
        print(saved_for_later)
        app.db.execute(
"""
DELETE FROM Cart
WHERE buyer_id = :buyer_id AND seller_id = :seller_id AND product_id = :product_id AND saved_for_later = :saved_for_later
RETURNING 1
""",
buyer_id = buyer_id, product_id = product_id, seller_id = seller_id, saved_for_later = saved_for_later)


# METHODS USED TO MOVE ITEMS BETWEEN CART AND SAVED FOR LATER STATUSES.

    # Method to move entries from saved for later to cart status.
    # @buyer_id is the owner of the entire cart.
    # @entries_to_move is an array of arrays with product IDs, seller IDs, total quantities in the cart for each item, and the # of quantities to move.
    @staticmethod
    def move_to_cart(buyer_id, entries_to_move):
        Cart._flip_saved_status(buyer_id, entries_to_move, "TRUE", "FALSE")

    # Same as the method above, except this moves entries from cart status to saved for later.
    @staticmethod
    def move_to_saved(buyer_id, entries_to_move):
        Cart._flip_saved_status(buyer_id, entries_to_move, "FALSE", "TRUE")

    # Private helper method that moves individual entries from one status to another.  
    @staticmethod       
    def _flip_saved_status(buyer_id, entries_to_move, current_status, destination_status):

        # Iterate over each entry that needs to be moved and extract data.
        for entry in entries_to_move:
            product_id = entry[0]
            seller_id = entry[1]
            total_quantity = entry[2]
            quantity_to_move = entry[3]

            # Check to see whether this entry is already in its destination status.
            quantity_in_cart = Cart._check_quantity_in_cart(buyer_id, product_id, seller_id, destination_status)

            # If the item is not in its destination, add it.
            if quantity_in_cart == 0:
                Cart._insert_into_cart(buyer_id, product_id, seller_id, quantity_to_move, destination_status)
                
            # If the item is in its destination, update it.
            else:
                new_quantity = quantity_in_cart + int(quantity_to_move)
                Cart._update_cart_quantity(buyer_id, product_id, seller_id, new_quantity, destination_status)
                
            # Now, remove the item from cart, since it is now in saved.

            # If all of the item was moved, delete the entry from cart.
            if quantity_to_move == total_quantity:
                Cart._delete_from_cart(buyer_id, product_id, seller_id, current_status)

            # If only some of the item was moved, keep the rest.
            else:
                new_quantity = int(total_quantity) - int(quantity_to_move)
                Cart._update_cart_quantity(buyer_id, product_id, seller_id, new_quantity, current_status)

    # Checks the quantity of an entry in the cart specified by:
    # @buyer_id is the ID of the owner of the the cart
    # @product_id is the ID of the product to move
    # @seller_id is the ID of the vendor of the product
    # @saved_for_later indicates whether the entry has cart status or saved for later. This is either "TRUE" or "FALSE".
    @staticmethod
    def _check_quantity_in_cart(buyer_id, product_id, seller_id, saved_for_later):
        rows = app.db.execute(
"""
SELECT quantity
FROM Cart
WHERE buyer_id = :buyer_id AND product_id = :product_id AND seller_id = :seller_id AND saved_for_later = :saved_for_later
""",
buyer_id = buyer_id, product_id = product_id, seller_id = seller_id, saved_for_later = saved_for_later)

        if rows == []:
            return 0
        else: 
            return rows[0][0]

    # Inserts an entry into Cart specifying a quantity of an entry.
    # Same parameter definitions as above, except for:
    # @quantity is the number of items of a certain product/seller combo that the buyer wants.
    @staticmethod
    def _insert_into_cart(buyer_id, product_id, seller_id, quantity, saved_for_later):
        app.db.execute(
"""
INSERT INTO Cart
VALUES (:buyer_id, :seller_id, :product_id, :quantity, :saved_for_later)
RETURNING 1
""",
buyer_id = buyer_id, product_id = product_id, seller_id = seller_id, quantity = quantity, saved_for_later=saved_for_later)

    # Updates a current entry in Cart with a new quantity for an entry.
    # Same parameter definitions as above, except for:
    # @new_quantity is the new amount the buyer wants.
    @staticmethod
    def _update_cart_quantity(buyer_id, product_id, seller_id, new_quantity, saved_for_later):
        app.db.execute(
"""
UPDATE Cart
SET quantity = :new_quantity
WHERE buyer_id = :buyer_id AND seller_id = :seller_id AND product_id = :product_id AND saved_for_later = :saved_for_later
RETURNING 1
""",
buyer_id = buyer_id, product_id = product_id, seller_id = seller_id, new_quantity = new_quantity, saved_for_later = saved_for_later)

    # Deletes an entry from Cart.
    # Same parameter definitions as above.
    @staticmethod
    def _delete_from_cart(buyer_id, product_id, seller_id, saved_for_later):
        app.db.execute(
"""
DELETE FROM Cart
WHERE buyer_id = :buyer_id AND seller_id = :seller_id AND product_id = :product_id AND saved_for_later = :saved_for_later
RETURNING 1
""",
buyer_id = buyer_id, product_id = product_id, seller_id = seller_id, saved_for_later = saved_for_later)

# METHODS USED TO UPDATE QUANTITIES FOR ENTRIES IN THE CART DATABASE.

    # Method to update the quantity for an item that is NOT saved for later.
    # Parameters have the same definitions as the methods above.
    @staticmethod
    def update_cart_quantity(buyer_id, entries_to_update):
        Cart._update_quantity(buyer_id, entries_to_update, "FALSE")
        
    # Method to update the quantity for an item that IS saved for later.
    # Parameters have the same definitions as the methods above.
    @staticmethod
    def update_saved_quantity(buyer_id, entries_to_update):
        Cart._update_quantity(buyer_id, entries_to_update, "TRUE")

    # Heper method used to access the Cart table and update it with a new quantity for an entry.
    # Parameters have the same definitions as the methods above.
    @staticmethod
    def _update_quantity(buyer_id, entries_to_update, saved_for_later):
        for cart_entry in entries_to_update:
            product_id = cart_entry[0]
            seller_id = cart_entry[1] 
            new_quantity = cart_entry[2]         

            # It is fair to assume that the entry is already in Cart, since it is coming directly from the Cart page.
            app.db.execute(
"""
UPDATE Cart
SET quantity = :new_quantity
WHERE buyer_id = :buyer_id AND seller_id = :seller_id AND product_id = :product_id AND saved_for_later = :saved_for_later
RETURNING 1
""",
buyer_id = buyer_id, product_id = product_id, seller_id = seller_id, new_quantity = new_quantity, saved_for_later = saved_for_later)












# GRAVEYARD

#     @staticmethod
#     def move_to_cart(buyer_id, entries_to_move):
#         for cart_entry in entries_to_move:
#             product_id = cart_entry[0]
#             seller_id = cart_entry[1]
#             total_quantity_in_saved = cart_entry[2]
#             quantity_to_move = cart_entry[3]

#             # Check to see whether this entry is already in the cart.
#             rows = app.db.execute("""
# SELECT quantity
# FROM Cart
# WHERE buyer_id = :buyer_id AND product_id = :product_id AND seller_id = :seller_id AND saved_for_later = FALSE
# """,
# buyer_id = buyer_id, product_id = product_id, seller_id = seller_id)

#             # The item is not in the immediate cart, so add it.
#             if rows == []:
#                 print('Entry is not in cart.')
#                 app.db.execute(
# """
# INSERT INTO Cart
# VALUES (:buyer_id, :seller_id, :product_id, :quantity, FALSE)
# RETURNING 1
# """,
# buyer_id = buyer_id, product_id = product_id, seller_id = seller_id, quantity = quantity_to_move)

#             # The item is in the immediate cart, so update it.
#             else:
#                 print('Entry is in cart.')
#                 current_quantity = rows[0][0]
#                 app.db.execute(
# """
# UPDATE Cart
# SET quantity = :new_quantity
# WHERE buyer_id = :buyer_id AND seller_id = :seller_id AND product_id = :product_id AND saved_for_later = FALSE
# RETURNING 1
# """,
# buyer_id = buyer_id, product_id = product_id, seller_id = seller_id, new_quantity= current_quantity + int(quantity_to_move))

#             # Remove the item from saved for later, since it is now in the cart.

#             # If all of the item was removed, delete the entry from saved for later.
#             if quantity_to_move == total_quantity_in_saved:
#                 print('All of item was moved.')
#                 app.db.execute(
# """
# DELETE FROM Cart
# WHERE buyer_id = :buyer_id AND seller_id = :seller_id AND product_id = :product_id AND saved_for_later = TRUE
# RETURNING 1
# """,
# buyer_id = buyer_id, product_id = product_id, seller_id = seller_id)

#             # If only some of the saved for later was moved, keep the rest.
#             else:
#                 print('Some of the item was moved.')
#                 app.db.execute(
# """
# UPDATE Cart
# SET quantity = :new_quantity
# WHERE buyer_id = :buyer_id AND seller_id = :seller_id AND product_id = :product_id AND saved_for_later = TRUE
# RETURNING 1
# """,
# buyer_id = buyer_id, product_id = product_id, seller_id = seller_id, new_quantity= int(total_quantity_in_saved) - int(quantity_to_move))
