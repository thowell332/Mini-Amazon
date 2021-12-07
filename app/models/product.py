from flask import current_app as app

class Product:
    def __init__(self, product_id, owner_id, description, name, image, category):
        self.product_id = product_id
        self.owner_id = owner_id
        self.description = description
        self.name = name
        self.image = image
        self.category = category

    @staticmethod
    def get(product_id):
        rows = app.db.execute('''
SELECT product_id, owner_id, description, name, image, category
FROM Product
WHERE product_id = :product_id
''',
                              product_id=product_id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    ##method to get all products
    def get_all():
        rows = app.db.execute('''
SELECT product_id, owner_id, description, name, image, category
FROM Product
''')
        return [Product(*row) for row in rows]

    @staticmethod
    ##method to return all products based on a certain search criteria
    def get_products_based_on_search_criteria(search_criteria):
        query = '''SELECT product_id, owner_id, description, name, image, category
        FROM Product
        WHERE name LIKE '%{0}%' OR description LIKE '%{0}%' OR category LIKE '%{0}%' '''.format(search_criteria)
        rows = app.db.execute(query)
        return [Product(*row) for row in rows] if rows is not None else None

    @staticmethod
    ##method to return all products in a certain category
    def get_products_based_on_category(category):
        query = '''SELECT product_id, owner_id, description, name, image, category
FROM Product
WHERE category LIKE '%{0}%'
        '''.format(category)
        rows = app.db.execute(query)
        return [Product(*row) for row in rows] if rows is not None else None

    @staticmethod
    ##A detailed product page will show all details for the product,
    ##together with a list of sellers and their current quantities in stock
    def get_product_display_page(product_id):
        rows = app.db.execute('''
SELECT p.product_id, p.owner_id, p.description, p.name, p.image, p.category, sp.price, COUNT(si.item_id)
FROM Product p, SellsProduct sp, SellsItem si
WHERE p.product_id = :product_id
AND p.product_id = sp.product_id
AND p.product_id = si.product_id
AND sp.seller_id = si.seller_id
GROUP BY p.product_id, sp.price
''', product_id=product_id)
        return [ProductDisplayPage(*row) for row in rows] if rows is not None else None

    @staticmethod
    ##A detailed product page will show all details for the product,
    ##together with a list of sellers and their current quantities in stock
    def get_product_display_page_price_ordered(product_id):
        rows = app.db.execute('''
SELECT p.product_id, p.owner_id, p.description, p.name, p.image, p.category, sp.price, COUNT(si.item_id)
FROM Product p, SellsProduct sp, SellsItem si
WHERE p.product_id = :product_id
AND p.product_id = sp.product_id
AND p.owner_id = sp.seller_id
AND p.product_id = si.product_id
AND p.owner_id = si.seller_id
GROUP BY p.product_id, sp.price
ORDER BY sp.price DESC
''', product_id=product_id)
        return [ProductDisplayPage(*row) for row in rows] if rows is not None else None

    @staticmethod
    ##A detailed product page will show all details for the product,
    ##together with a list of sellers and their current quantities in stock
    def get_product_display_page_quantity_ordered(product_id):
        rows = app.db.execute('''
SELECT p.product_id, p.owner_id, p.description, p.name, p.image, p.category, sp.price, COUNT(si.item_id)
FROM Product p, SellsProduct sp, SellsItem si
WHERE p.product_id = :product_id
AND p.product_id = sp.product_id
AND p.owner_id = sp.seller_id
AND p.product_id = si.product_id
AND p.owner_id = si.seller_id
GROUP BY p.product_id, sp.price
ORDER BY COUNT(si.item_id) DESC
''', product_id=product_id)
        return [ProductDisplayPage(*row) for row in rows] if rows is not None else None

    @staticmethod
    ##Method to insert a new product into the database
    def insert_new_product(product_id, owner_id, description, name, image, category):
        insert_statement = '''
INSERT INTO Product (product_id, owner_id, description, name, image, category)
VALUES (%s, %s, %s, %s, %s, %s)
        '''
        values = (product_id, owner_id, description, name, image, category)
        try:
            rows = app.db.execute("""
INSERT INTO Product(product_id, owner_id, description, name, image, category)
VALUES(:product_id, :owner_id, :description, :name, :image, :category)
RETURNING product_id
""",
                                  product_id=product_id,
                                  owner_id=owner_id,
                                  description=description,
                                  name=name,
                                  image=image,
                                  category=category)
            return product_id
        except Exception as e:
            print(e)
            return None

    @staticmethod
    ##Method to delete a product from the database
    def delete_product(product_id):
        try:
            app.db.execute('''
DELETE FROM Product WHERE product_id = :product_id
        ''', product_id=product_id)
        except Exception as e:
            print(e)


class ProductDisplayPage:
    def __init__(self, product_id, owner_id, description, name, image, category, price, quantity):
        self.product_id = product_id
        self.owner_id = owner_id
        self.description = description
        self.name = name
        self.image = image
        self.category = category
        self.price = price
        self.quantity = quantity

