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
    def __init__(self, product_name, product_image, seller_first_name, seller_last_name, saved_for_later, quantity, unit_price):
        self.product_name = product_name
        self.product_image = product_image
        self.seller_name = seller_first_name + ' ' + seller_last_name
        self.saved_for_later = saved_for_later
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
BasicCart(product_id, seller_id, saved_for_later, quantity) AS (
    SELECT product_id, seller_id, saved_for_later, quantity
    FROM Cart
    WHERE buyer_id = :buyer_id
),

CartAddPrice(product_id, seller_id, saved_for_later, quantity, unit_price) AS (
    SELECT BasicCart.product_id, BasicCart.seller_id, BasicCart.saved_for_later, BasicCart.quantity, SellsProduct.price
    FROM BasicCart
    LEFT JOIN
    SellsProduct
    ON BasicCart.seller_id = SellsProduct.seller_id AND BasicCart.product_id = SellsProduct.product_id
),

CartAddProduct(product_name, product_image, seller_id, saved_for_later, quantity, unit_price) AS (
    SELECT Product.name, Product.image, CartAddPrice.seller_id, CartAddPrice.saved_for_later, CartAddPrice.quantity, CartAddPrice.unit_price
    FROM CartAddPrice
    LEFT JOIN
    Product
    ON CartAddPrice.product_id = Product.product_id
),

FullCart(product_name, product_image, seller_first_name, seller_last_name, saved_for_later, quantity, unit_price) AS (
    SELECT CartAddProduct.product_name, CartAddProduct.product_image, Account.firstname, Account.lastname, CartAddProduct.saved_for_later, CartAddProduct.quantity, CartAddProduct.unit_price
    FROM CartAddProduct
    LEFT JOIN
    Account
    ON CartAddProduct.seller_id = Account.account_id
)
Select * FROM FullCart
""",

                              buyer_id = buyer_id)

        print('rows')
        print(rows)

        if not rows:  # email not found
            return []
        else:
            return [CartItem(*row) for row in rows]


    # TODO: MAKE THIS SERIALIZABLE AND A PROCEDURE.
    @staticmethod
    def purchase_by_buyer_id(buyer_id):
        print('TEST')
