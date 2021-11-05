from flask import current_app as app

class userProductReview:
    def __init__(self, product_id, num_stars, date, description):
        self.product_id = product_id
        self.num_stars = num_stars
        self.date = date
        self.description = description

    @staticmethod
    ##method to get all product reviews written by user with user_id
    def get(user_id):
        rows = app.db.execute('''
SELECT product_id, num_stars, date, description
FROM ProductReview
WHERE buyer_id = :user_id
''',
                              user_id=user_id)
        print(rows)
        return [userProductReview(*row) for row in rows] if rows is not None else None


    @staticmethod
    ##Method to update a selected product review authored by user with user_id
    def update_product_review(user_id, product_id, num_stars, date, description):
        try: app.db.execute('''
UPDATE ProductReview SET (num_stars, date, description) = (:num_stars, :date, :description)
WHERE buyer_id = :user_id AND product_id = :product_id
        ''', user_id=user_id, product_id=product_id, num_stars=num_stars, date=date, description=description)
        except Exception as e:
            print(e)

    @staticmethod
    ##Method to delete a selected product review authored by user with user_id
    def delete_product_review(user_id, product_id):
        try: app.db.execute('''
DELETE FROM ProductReview WHERE buyer_id = :user_id AND product_id = :product_id
        ''', user_id=user_id, product_id=product_id)
        except Exception as e:
            print(e)

class userSellerReview:
    def __init__(self, product_id, num_stars, date, description):
        self.product_id = product_id
        self.num_stars = owner_id
        self.date = date
        self.description = description

    @staticmethod
    ##method to get all product reviews written by user with user_id
    def get(user_id):
        rows = app.db.execute('''
SELECT product_id, num_stars, date, description
FROM ProductReview
WHERE buyer_id = :user_id
''',
                              user_id=user_id)
        return [userProductReview(*row) for row in rows] if rows is not None else None


    @staticmethod
    ##Method to update a selected product review authored by user with user_id
    def update_product_review(user_id, product_id, num_stars, date, description):
        try: app.db.execute('''
UPDATE ProductReview SET (num_stars, date, description) = (:num_stars, :date, :description)
WHERE buyer_id = :user_id AND product_id = :product_id
        ''', user_id=user_id, product_id=product_id, num_stars=num_stars, date=date, description=description)
        except Exception as e:
            print(e)

    @staticmethod
    ##Method to delete a selected product review authored by user with user_id
    def delete_product_review(user_id, product_id):
        try: app.db.execute('''
DELETE FROM ProductReview WHERE buyer_id = :user_id AND product_id = :product_id
        ''', user_id=user_id, product_id=product_id)
        except Exception as e:
            print(e)

class UserProductReviewDisplayPage:
    def __init__(self, user_id, product_id, num_stars, date, description):
        self.user_id = user_id
        self.product_id = product_id
        self.num_stars = num_stars
        self.date = date
        self.description = description
 

