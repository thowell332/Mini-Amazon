from flask import current_app as app


class PurchaseSummary:
    def __init__(self, purchase_id, date, status):
        self.purchase_id = purchase_id
        self.date = date
        self.status = status

class PurchaseEntry:
    def __init__(self, product_name, product_image, seller_name, quantity, unit_price):
        self.product_name = product_name
        self.product_image = product_image
        self.seller_name = seller_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = quantity * unit_price

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
    def _add_to_purchase(buyer_id, product_id, item_id, purchase_id, status, date):
        app.db.execute(
"""
INSERT INTO Purchase (buyer_id, product_id, item_id, purchase_id, status, date)
VALUES (:buyer_id, :product_id, :item_id, :purchase_id, :status, :date)
RETURNING 1
""",
        buyer_id = buyer_id, product_id = product_id, item_id = item_id, purchase_id = purchase_id, status = status, date = date)

    # Method used to get all purchase IDs and dates for those purchases.
    # Same parameter definitions as the methods above.
    @staticmethod
    def _get_purchases(buyer_id):
        rows = app.db.execute(
"""
SELECT MIN(status)
FROM Purchase
WHERE buyer_id = :buyer_id
GROUP BY purchase_id, date
""",
        buyer_id = buyer_id)

        return [PurchaseSummary(*row) for row in rows]
