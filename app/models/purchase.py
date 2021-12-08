from flask import current_app as app

# Status is either 0, 1, or 2 in the database.
# This maps to either "ordered", "shipped", or "fulfilled"
status_options = ["ORDERED", "SHIPPED", "DELIVERED"]

# Class used to show each purchase made.
class PurchaseSummary:
    def __init__(self, purchase_id, date, status):
        self.purchase_id = purchase_id
        self.date = date.strftime("%m/%d/%Y at %H:%M:%S")
        self.status = status_options[status]

# Class used to show each item in a purchase.
class PurchaseEntry:
    def __init__(self, product_name, product_image, seller_first_name, seller_last_name, seller_id, quantity, status, unit_price):
        self.product_name = product_name
        self.product_image = product_image
        self.seller_name = seller_first_name + ' ' + seller_last_name
        self.seller_id = seller_id
        self.quantity = quantity
        self.unit_price = unit_price
        # Round the price to avoid floating point errors.
        self.total_price = round(quantity * unit_price, 2)
        self.status = status_options[status]

# Methods used to query the purchase database.
class Purchase:

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
    def _add_to_purchase(buyer_id, seller_id, product_id, item_id, purchase_id, status, date, price):
        app.db.execute(
            """
            INSERT INTO Purchase (buyer_id, seller_id, product_id, item_id, purchase_id, status, date, price)
            VALUES (:buyer_id, :seller_id, :product_id, :item_id, :purchase_id, :status, :date, :price)
            RETURNING 1
            """,
        buyer_id = buyer_id, seller_id = seller_id, product_id = product_id, item_id = item_id, purchase_id = purchase_id, status = status, date = date, price = price)

    # Method used to get all purchase IDs, dates, and statuses for those purchases.
    # Status is the minimum for all items with the purchase_ID.
    # Same parameter definitions as the methods above.
    @staticmethod
    def _get_purchases(buyer_id):
        rows = app.db.execute(
            """
            SELECT purchase_id, date, MIN(status)
            FROM Purchase
            WHERE buyer_id = :buyer_id
            GROUP BY purchase_id, date
            ORDER BY date DESC
            """,
        buyer_id = buyer_id)

        return [PurchaseSummary(*row) for row in rows]

    # Method used to get all products and  for those purchases.
    # Status is the minimum for all items with the purchase_ID.
    # Same parameter definitions as the methods above.
    @staticmethod
    def _get_individual_purchase(buyer_id, purchase_id):
        rows = app.db.execute(
            """
            WITH
            BasicPurchase(product_id, seller_id, quantity, min_status, price) AS (
                SELECT product_id, seller_id, COUNT(item_id), MIN(status), price
                FROM Purchase
                WHERE buyer_id = :buyer_id AND purchase_id = :purchase_id
                GROUP BY product_id, seller_id, date, price
            ),
            PurchaseAddProduct(product_name, product_image, seller_id, quantity, min_status, price) AS (
                SELECT Product.name, Product.image, BasicPurchase.seller_id, BasicPurchase.quantity, BasicPurchase.min_status, BasicPurchase.price
                FROM BasicPurchase
                LEFT JOIN
                Product
                ON BasicPurchase.product_id = Product.product_id
            ),
            PurchaseAddSeller(product_name, product_image, seller_firstname, seller_lastname, seller_id, quantity, min_status, price) AS (
                SELECT PurchaseAddProduct.product_name, PurchaseAddProduct.product_image, Account.firstname, Account.lastname, PurchaseAddProduct.seller_id, PurchaseAddProduct.quantity, PurchaseAddProduct.min_status, PurchaseAddProduct.price
                FROM PurchaseAddProduct
                LEFT JOIN
                Account
                ON PurchaseAddProduct.seller_id = Account.account_id
            )
            SELECT * FROM PurchaseAddSeller
            """,
        buyer_id = buyer_id, purchase_id = purchase_id)

        return [PurchaseEntry(*row) for row in rows]

    # Helper method used to get the total cost of a user's purchase.
    # Same parameter definitions as the methods above.
    @staticmethod
    def _get_total_purchase_cost(buyer_id, purchase_id):

        purchase_entries = Purchase._get_individual_purchase(buyer_id, purchase_id)
        total_purchase_cost = 0.0

        for entry in purchase_entries:
            total_purchase_cost += float(entry.total_price)

        return round(total_purchase_cost, 2)