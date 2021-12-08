from flask import current_app as app

# Class representing an entry in SellsItem.
# @product_id is the product being solld.
# @seller_id is the seller of the product.
# @item_id is the actual item being sold.
class SellsItem:
    def __init__(self, seller_id, product_id, item_id):
        self.seller_id = seller_id
        self.product_id = product_id
        self.item_id = item_id

    # Helper method used to count how many items are in a seller's inventory.
    # This is used to determine which items are in stock vs out of stock.
    # Parameter definitions are the same as above.
    @staticmethod
    def _get_inventory_count(product_id, seller_id):
        rows = app.db.execute(
"""
SELECT COUNT(*)
FROM SellsItem
WHERE product_id = :product_id AND seller_id = :seller_id
""",
    product_id = product_id, seller_id = seller_id)

        return rows[0][0]


    # Helper method used to get all items sold for a product and seller.
    # Parameter definitions are the same as above.
    @staticmethod
    def _get_full_inventory(product_id, seller_id):
        rows = app.db.execute(
"""
SELECT *
FROM SellsItem
WHERE product_id = :product_id AND seller_id = :seller_id
""",
product_id = product_id, seller_id = seller_id)

        # If no items are being sold, return None.
        if rows is None:
            return []
        # Otherwise, return the information via SellsItem objects.
        else:
            return [SellsItem(*row) for row in rows]

    # Helper method used to delete an item from SellsItem, indicating it has been purchased.
    # Parameter definitions are the same as above.
    @staticmethod
    def _delete_from_sells_item(seller_id, product_id, item_id):
        app.db.execute(
"""
DELETE
FROM SellsItem
WHERE seller_id = :seller_id AND product_id = :product_id AND item_id = :item_id
RETURNING 1
""",
        seller_id = seller_id, product_id = product_id, item_id = item_id)