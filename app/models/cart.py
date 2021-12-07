from flask import current_app as app
from datetime import datetime

from .user import User
from .sellsItem import SellsItem
 
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
    def get_cart(buyer_id):
        return Cart._get_info(buyer_id, "FALSE")
        
    # Gets all the items in the cart that ARE saved for later.
    # @buyer_id is the owner of the cart.
    @staticmethod
    def get_saved(buyer_id):
        return Cart._get_info(buyer_id, "TRUE")

    # Gets all the items in the cart that are either saved for later or not, depending on the parameter.
    # @saved_for_later is either "TRUE" or "FALSE", depending on whether we are interested in saved for later items or not, respectively.
    @staticmethod
    def _get_info(buyer_id, saved_for_later):
        
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


# METHODS TO PURCHASE THE CART

    # Purchase the entire cart for the user.
    # @buyer_id is the ID of the owner of the cart.
    @staticmethod
    def purchase_cart(buyer_id):

        # Get information for entries in the users cart.
        cart_entries = Cart._get_info(buyer_id, "FALSE")

        # Determine which items are in stock and out of stock.
        out_of_stock = []
        in_stock = []

        for entry in cart_entries:
            inventory_count = SellsItem._get_inventory_count(entry.product_id, entry.seller_id)

            if entry.quantity > inventory_count:
                out_of_stock.append([entry, inventory_count])
            else:
                in_stock.append(entry)

        # Check to see if the user is puruchasing out of stock items.
        # If they are, block the purchase.
        if len(out_of_stock) > 0:
            return ['Inventory Error', out_of_stock]
        
        # Check to see if the user has enough money to purchase the items.
        # If they don't, block the purchase.
        total_cart_cost = Cart.get_total_cart_cost(buyer_id)
        current_balance = float(User.get_balance(buyer_id))

        if total_cart_cost > current_balance:
            return ['Balance Error', current_balance]
        
        # At this point, the purchase can be successful! So, execute it.

        # Create a unique purchase ID.
        purchase_id = Cart._create_purchase_id()

        # Set the status for purchases 0, meaning the items have been ordered.
        # TODO: CHANGE TO 0
        initial_status = "ordered"

        # Purchase all the in stock items.

        # First, charge the user's balance.
        new_balance = current_balance - total_cart_cost
        User.update_balance(buyer_id, new_balance)
        
        # Next, iterate over each type of product/seller combo being purchased.
        for entry in in_stock:

            # Remove the product/seller combo from the Cart table.
            Cart._delete_from_db(buyer_id, entry.product_id, entry.seller_id, "FALSE")

            # Get the inventory being sold.
            inventory = SellsItem._get_full_inventory(entry.product_id, entry.seller_id)

            # Buy one item from inventory for each incremental quantity selected.
            for i in range(entry.quantity):
                purchased_item = inventory[i]
                SellsItem._delete_from_sells_item(purchased_item.item_id)
                Cart._add_to_purchase(buyer_id, entry.product_id, purchased_item.item_id, purchase_id, initial_status)

            # Pay the seller for the items purchased.
            User.update_balance(entry.seller_id, entry.total_price)
        
        return ["Success"]

    # Helper method used to create a unique purchase ID.
    # This is just the maximum ID already created incremented by one.
    @staticmethod
    def _create_purchase_id():
        rows = app.db.execute(
"""
SELECT MAX(purchase_id)
FROM Purchase
""")
        # If there are no purchases, start with an ID of 1.
        count = rows[0][0]
        if count is None:
            return 1
        else:
            return count + 1

    # Helper method used to add an entry to Purchase, indicating it has been bought officially.
    # Same parameter definitions as the methods above, except for:
    # @purchase_id is the ID of the purchase being exectured
    # @status is the status of the item being purchased (0, 1, or 2).
    @staticmethod
    def _add_to_purchase(buyer_id, product_id, item_id, purchase_id, status):
        app.db.execute(
"""
INSERT INTO Purchase (buyer_id, product_id, item_id, purchase_id, status, date)
VALUES (:buyer_id, :product_id, :item_id, :purchase_id, :status, :date)
RETURNING 1
""",
        buyer_id = buyer_id, product_id = product_id, item_id = item_id, purchase_id = purchase_id, status = status, date = datetime.now())


    # Helper method used to get the total cost of a user's cart.
    # Same parameter definitions as the methods above.
    @staticmethod
    def get_total_cart_cost(buyer_id):
        cart_entries = Cart.get_cart(buyer_id)
        total_cart_cost = 0.0

        for entry in cart_entries:
            total_cart_cost += float(entry.total_price)

        return total_cart_cost

 