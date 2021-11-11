from flask import current_app as app

class Inventory:
    def __init__(self, name, description, image, price, quantity):
        self.name = name
        self.description = description
        self.image = image
        self.price = price
        self.quantity = quantity

    @staticmethod
    # Retrieve seller inventory
    def get(seller_id):
        rows = app.db.execute('''
SELECT p.name, p.description, p.image, sp.price, COUNT(si.item_id) as quantity
FROM Product p, SellsItem si, SellsProduct sp
WHERE si.seller_id = :seller_id AND p.product_id = si.product_id
AND sp.seller_id = :seller_id AND p.product_id = sp.product_id
GROUP BY p.name, p.description, p.image, sp.price;
''',
                              seller_id=seller_id)
        return [Inventory(*row) for row in rows] if rows is not None else None

    @staticmethod
    # Update product listing
    def update_product_listing(seller_id, product_id, price):
        try: app.db.execute('''
UPDATE SellsProduct SET price = :price
WHERE seller_id = :seller_id AND product_id = :product_id
        ''', seller_id=seller_id, product_id=product_id, price=price)
        except Exception as e:
            print(e)
