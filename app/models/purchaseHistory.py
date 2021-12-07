from flask import current_app as app

class PurchaseHistory:
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
        print('HEys')