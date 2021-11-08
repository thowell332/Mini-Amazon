from flask import current_app as app

# TODO: Convert from normal query to procedure.
class CartItem:
    def __init__(self, product_name, product_image, seller_name, quantity, unit_price):
        self.product_name = product_name
        self.product_image = product_image
        self.seller_name = seller_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = self.unit_price * self.quantity

class Cart:
    def __init__(self, product_id, seller_id, quantity):
        self.product_id = product_id
        self.seller_id = seller_id
        self.quantity = quantity

    @staticmethod
    def initialize_get_procedure():
        app.db.execute("""
CREATE PROCEDURE GetById
AS
(WITH
CartInfo(product_id, seller_id, quantity) AS (
    SELECT product_id, seller_id, quantity
    FROM Cart
    WHERE buyer_id = $1
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
    SELECT CartInfoProduct.product_name, CartInfoProduct.product_image, Account.name, CartInfoProduct.quantity, CartInfoProduct.unit_price
    FROM CartInfoProduct
    LEFT JOIN
    Account
    ON CartInfoProduct.seller_id = Account.account_id
)
Select * FROM CartInfoProduct)
""")

    @staticmethod
    def get_by_buyer_id(buyer_id):
        rows = app.db.execute("""CALL GetById(:buyer_id)""", buyer_id = buyer_id)
        if not rows:  # email not found
            return None
        else:
            return [CartItem(*row) for row in rows]

    # TODO: MAKE THIS SERIALIZABLE AND A PROCEDURE.
    @staticmethod
    def purchase_by_buyer_id(buyer_id):
        print('TEST')

        