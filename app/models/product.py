from flask import current_app as app

class Product:
    def __init__(self, product_id, owner_id, description, name, image, category):
        self.product_id = product_id
        self.owner_id = owner_id
        self.description = description
        self.name = name
        self.image = image
        self.category = category

    # Method to get a product based on a product id
    # @param product_id- the product id being searched for.
    # @return- all products with product_id = @param product_id.
    @staticmethod
    def get(product_id):
        rows = app.db.execute('''
SELECT product_id, owner_id, description, name, image, category
FROM Product
WHERE product_id = :product_id
''',
                              product_id=product_id)
        return Product(*(rows[0])) if rows is not None else None

    # Method to get all products in the database.
    # @return- all products.
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT product_id, owner_id, description, name, image, category
FROM Product
''')
        return [Product(*row) for row in rows]

    # Method to return all products based on a certain search criteria
    # @param search_criteria- the search criteria to get the products.
    # @return- all products related to the search criteria.
    @staticmethod
    def get_products_based_on_search_criteria(search_criteria):
        query = '''SELECT product_id, owner_id, description, name, image, category
        FROM Product
        WHERE name LIKE '%{0}%' OR description LIKE '%{0}%' OR category LIKE '%{0}%' '''.format(search_criteria)
        rows = app.db.execute(query)
        return [Product(*row) for row in rows] if rows is not None else None

    # Method to get all products based on a category.
    # @param category- the category the products are in.
    # @return- all products related to the category being searched for.
    @staticmethod
    def get_products_based_on_category(category):
        query = '''SELECT product_id, owner_id, description, name, image, category
FROM Product
WHERE category LIKE '%{0}%'
        '''.format(category)
        rows = app.db.execute(query)
        return [Product(*row) for row in rows] if rows is not None else None

    # Method to get a product display page based on a product id.
    # This detailed product page show all details for the product,
    # together with a list of sellers and their current quantities in stock
    # @param product_id- the product id being searched for.
    # @return- a list of products with all of the necessary details to display on the product page.
    @staticmethod
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

    # Method to get a product display page based on a product id, but sorted by price.
    # This detailed product page show all details for the product,
    # together with a list of sellers and their current quantities in stock
    # @param product_id- the product id being searched for.
    # @return- a price ordered list of products with all of the necessary details to display on the product page.
    @staticmethod
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

    # Method to get a product display page based on a product id, but sorted by quantity.
    # This detailed product page show all details for the product,
    # together with a list of sellers and their current quantities in stock
    # @param product_id- the product id being searched for.
    # @return- a quantity ordered list of products with all of the necessary details to display on the product page.
    @staticmethod
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

    # Method to insert a new product into the database.
    # @param product_id- the product id of the new product.
    # @param owner_id- the owner of the product being created.
    # @param description- a description of the product.
    # @param name- the name of the product.
    # @param image- the image string of the product.
    # @param category- the category the product belongs to.
    # @return- the product id that has been inserted.
    @staticmethod
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

    # Method to delete a product from a database.
    # @param product_id- the product id of the product to be deleted.
    @staticmethod
    def delete_product(product_id):
        try:
            app.db.execute('''
DELETE FROM Product WHERE product_id = :product_id
        ''', product_id=product_id)
        except Exception as e:
            print(e)


# A class to containing all of the information to display a specific product.
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

