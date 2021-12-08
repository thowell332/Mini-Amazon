from flask import current_app as app
import sys

class Inventory:
    def __init__(self, product_id, name, description, image, price, quantity):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.image = image
        self.price = price
        self.quantity = quantity
    
    @staticmethod
    # retrieve seller inventory
    def get(seller_id):
        rows = app.db.execute(
            '''
            SELECT t1.product_id, t1.name, t1.description, t1.image, t1.price, COALESCE(t2.quantity, 0) as quantity
            FROM
            (
                SELECT p.product_id, p.name, p.description, p.image, sp.price
                FROM Product p, SellsProduct sp
                WHERE sp.seller_id = :seller_id AND p.product_id = sp.product_id
            ) AS t1 LEFT OUTER JOIN
            (
                SELECT p.product_id, p.name, p.description, p.image, sp.price, COUNT(si.item_id) as quantity
                FROM Product p, SellsItem si, SellsProduct sp
                WHERE si.seller_id = :seller_id AND p.product_id = si.product_id
                AND sp.seller_id = :seller_id AND p.product_id = sp.product_id
                GROUP BY p.product_id, p.name, p.description, p.image, sp.price
            ) AS t2 ON t1.product_id = t2.product_id;
            ''',
            seller_id=seller_id
        )
        return [Inventory(*row) for row in rows] if rows is not None else None


class InventoryListing:
    def __init__(self, name, description, price, quantity):
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity

    @staticmethod
    # retrieve product listing information
    def get_product_listing(seller_id, product_id):
        row = app.db.execute(
            '''
            SELECT t1.name, t1.description, t1.price, COALESCE(t2.quantity, 0) as quantity
            FROM
            (
                SELECT p.product_id, p.name, p.description, sp.price
                FROM Product p, SellsProduct sp
                WHERE sp.seller_id = :seller_id AND sp.product_id = :product_id
                AND p.product_id = :product_id 
            ) AS t1 LEFT OUTER JOIN
            (
                SELECT p.product_id, p.name, p.description, sp.price, COUNT(si.item_id) as quantity
                FROM Product p, SellsItem si, SellsProduct sp
                WHERE si.seller_id = :seller_id AND si.product_id = :product_id
                AND sp.seller_id = :seller_id AND sp.product_id = :product_id
                AND p.product_id = :product_id
                GROUP BY p.product_id, p.name, p.description, sp.price
            ) AS t2 ON t1.product_id = t2.product_id;
            ''',
            product_id=product_id,
            seller_id=seller_id)
        return InventoryListing(*(row[0])) if row else None

    @staticmethod
    # update existing product listing
    def edit_product_listing(seller_id, product_id, price, delta_quantity):
        # update the price of the product for the seller
        try: app.db.execute(
            '''
            UPDATE SellsProduct SET price = :price
            WHERE seller_id = :seller_id AND product_id = :product_id;
            ''',
            seller_id=seller_id,
            product_id=product_id,
            price=price
        )
        except Exception as e:
            print(e)
        # update quantity of the product for the seller
        InventoryListing.update_quantity(seller_id, product_id, delta_quantity)

    @staticmethod
    # add new product listing
    def add_product_listing(seller_id, form):
        # get product id for this listing
        row = app.db.execute(
            '''
            SELECT product_id
            FROM Product
            WHERE name = :name;
            ''',
            name=form.name.data
        )
        product_id = row[0][0] if row is not None else None
        
        # update SellsProduct with new listing
        try: app.db.execute(
            '''
            INSERT INTO SellsProduct
            VALUES (:seller_id, :product_id, :price)
            ''',
            seller_id=seller_id,
            product_id=product_id,
            price=form.price.data
        )     
        except Exception as e:
            print(e)

        # add new items for sale to match quantity
        InventoryListing.update_quantity(seller_id, product_id, form.quantity.data)
    
    @staticmethod
    # delete existing product listing
    def delete_product_listing(seller_id, product_id):
        # remove all items associated with this listing
        try: app.db.execute(
            '''
            DELETE FROM SellsItem
            WHERE seller_id = :seller_id AND product_id = :product_id
            ''',
            seller_id=seller_id,
            product_id=product_id
        )
        except Exception as e:
            print(e)
        
        # remove product listing from SellsProduct
        try: app.db.execute(
            '''
            DELETE FROM SellsProduct
            WHERE seller_id = :seller_id AND product_id = :product_id
            ''',
            seller_id=seller_id,
            product_id=product_id
        )
        except Exception as e:
            print(e)
    
    @staticmethod
    def update_quantity(seller_id, product_id, delta_quantity):
        # if new quantity is lower, remove items
        if delta_quantity < 0:
            # remove items in descending order of item_id
            try: app.db.execute(
                '''
                DELETE FROM SellsItem s1
                WHERE s1.item_id IN (
                    SELECT s2.item_id
                    FROM SellsItem s2
                    WHERE s2.seller_id = :seller_id AND s2.product_id = :product_id
                    ORDER BY s2.item_id DESC LIMIT :delta
                );
                ''',
                seller_id=seller_id,
                product_id=product_id,
                delta=abs(delta_quantity)
            )
            except Exception as e:
                print(e)
        # if new quantity is higher, add items
        elif delta_quantity > 0:
            # get existing item_id values
            rows = app.db.execute(
                '''
                SELECT item_id
                FROM SellsItem
                WHERE product_id = :product_id
                ORDER BY item_id;
                ''',
                seller_id=seller_id,
                product_id=product_id
            )
            current_items = [row[0] for row in rows] if rows else [0]
            # assign item_id values to the new rows
            new_items = [max(current_items) + i + 1 for i in range(delta_quantity)]
            # generate row values to be inserted
            values = ', '.join(['(' + ', '.join((str(seller_id), str(product_id), str(new_items[i]))) + ')' for i in range(delta_quantity)])
            # execute insert query
            try: app.db.execute(
                '''
                INSERT INTO SellsItem
                VALUES 
                ''' + values
            )
            except Exception as e:
                print(e)

