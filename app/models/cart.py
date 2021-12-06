from flask import current_app as app
from datetime import datetime

class CartEntry:
    def __init__(self, buyer_id, seller_id, product_id, quantity):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.product_id = product_id
        self.quantity = quantity

class SellsItemEntry:
    def __init__(self, seller_id, product_id, item_id):
        self.seller_id = seller_id
        self.product_id = product_id
        self.item_id = item_id

# TODO: Convert from normal query to procedure.
class CartItem:
    def __init__(self, product_name, product_image, seller_name, quantity, unit_price):
        self.product_name = product_name
        self.product_image = product_image
        self.seller_name = seller_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = self.unit_price * self.quantity

# TODO: Refactor SQL queries to remove overlap.
class Cart:
    def __init__(self, product_id, seller_id, quantity):
        self.product_id = product_id
        self.seller_id = seller_id
        self.quantity = quantity

    @staticmethod
    def get_cart_for_buyer_id(buyer_id):
        rows = app.db.execute("""
WITH
CartInfo(product_id, seller_id, quantity) AS (
    SELECT product_id, seller_id, quantity
    FROM Cart
    WHERE buyer_id = :buyer_id
),

CartInfoSellsProduct(product_id, seller_id, quantity, unit_price) AS (
    SELECT CartInfo.product_id, CartInfo.seller_id, CartInfo.quantity, SellsProduct.price
    FROM CartInfo
    LEFT JOIN
    SellsProduct
    ON CartInfo.seller_id = SellsProduct.seller_id AND CartInfo.product_id = SellsProduct.product_id
),

CartInfoProduct(product_name, product_image, seller_id, quantity) AS (
    SELECT Product.name, Product.image, CartInfoSellsProduct.seller_id, CartInfoSellsProduct.quantity, CartInfoSellsProduct.unit_price
    FROM CartInfoSellsProduct
    LEFT JOIN
    Product
    ON CartInfoSellsProduct.product_id = Product.product_id
),

CartInfoSeller(product_name, product_image, seller_name, quantity) AS (
    SELECT CartInfoProduct.product_name, CartInfoProduct.product_image, Account.firstname, CartInfoProduct.quantity, CartInfoProduct.unit_price
    FROM CartInfoProduct
    LEFT JOIN
    Account
    ON CartInfoProduct.seller_id = Account.account_id
)
Select * FROM CartInfoProduct
""",

buyer_id = buyer_id)

        if not rows:  # email not found
            return []
        else:
            return [CartItem(*row) for row in rows]


    # TODO: Make this serializable.
    @staticmethod
    def purchase_cart_for_buyer_id(buyer_id):
        cart_tuples = app.db.execute(
"""
SELECT *
FROM Cart
WHERE buyer_id = :buyer_id
""",
buyer_id = buyer_id)


        cart_items = [CartEntry(*cart_tuple) for cart_tuple in cart_tuples]

        out_of_stock_items = []
        in_stock_items = []

        for item in cart_items:
            quantity_in_inventory = app.db.execute(
"""
SELECT COUNT(*)
FROM SellsItem
WHERE product_id = :product_id AND seller_id = :seller_id
""",
product_id = item.product_id, seller_id = item.seller_id)

            quantity_in_inventory = quantity_in_inventory[0][0]
            if item.quantity > quantity_in_inventory or item.quantity == 0:
                out_of_stock_items.append(item)
            else:
                in_stock_items.append(item)
            
            # Purchase all the in stock items and remove them form cart.

            # TODO: Make purchase ID unique.
            purchase_id = 123
            initial_status = 'Unfulfilled'

            for item in in_stock_items:

                # Remove product from Cart table.
                app.db.execute(
"""
DELETE
FROM Cart
WHERE product_id = :product_id AND seller_id = :seller_id AND buyer_id = :buyer_id
RETURNING 0
""",

product_id = item.product_id, seller_id = item.seller_id, buyer_id  = buyer_id)

                # Remove item from SellsItem table.
                items_available_for_purchase = app.db.execute(
"""
SELECT *
FROM SellsItem
WHERE product_id = :product_id AND seller_id = :seller_id
""",
product_id = item.product_id, seller_id = item.seller_id)


                items_avaiable_for_purchase = [SellsItemEntry(*item_available) for item_available in items_available_for_purchase]
        
                # Buy one item for each incremental quantity selected.
                
                for i in range(item.quantity):
                    purchased_item = items_avaiable_for_purchase[i]

                    # Remove the item as being for sale.
                    app.db.execute(
"""
DELETE
FROM SellsItem
WHERE item_id = :item_id
RETURNING 0
""",
item_id = purchased_item.item_id)

                    # TODO: Fix the code below. SQL thinks purchase doesn't exist.
                    # Note that the item was purchased.
                    # app.db.execute(
                    # """
                    # INSERT INTO Purchase (buyer_id, product_id, item_id, purchase_id, status, date)
                    # VALUES (:buyer_id, :product_id, :item_id, :purchase_id, :status, :date)
                    # RETURNING 0
                    # """,
                    # buyer_id = buyer_id, product_id = purchased_item.product_id, item_id = purchased_item.item_id, purchase_id = purchase_id, status = initial_status, date = datetime.now())



