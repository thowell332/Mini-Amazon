from flask import current_app as app

class Product:
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT product_id
FROM Product
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT product_id
FROM Product
'''
                              )
        return [Product(*row) for row in rows]
