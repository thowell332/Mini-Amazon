from flask import current_app as app

class userProductReview:
    def __init__(self, product_id, product_name, seller_id, seller_fname, seller_lname, num_stars, date, description, upvotes, images):
        self.product_id = product_id
        self.product_name = product_name
        self.seller_id = seller_id
        self.seller_name = seller_fname + ' ' + seller_lname
        self.num_stars = num_stars
        self.date = date
        self.description = description
        self.upvotes = upvotes
        self.images = images

    @staticmethod
    ##method to get all product reviews written by user with user_id in reverse chronological order
    def get(user_id):
        rows = app.db.execute('''
SELECT pr.product_id, p.name, pr.seller_id, a.firstname, a.lastname, num_stars, date, pr.description, upvotes, pr.images
FROM ProductReview pr, Product p, Account a
WHERE pr.buyer_id = :user_id
AND pr.product_id = p.product_id
AND pr.seller_id = a.account_id
ORDER BY date DESC
''',
                              user_id=user_id)
        return [userProductReview(*row) for row in rows] if rows is not None else None

    @staticmethod
    ##Method to submit a product review authored by user with user_id
    def submit_product_review(user_id, product_id, seller_id, num_stars, date, description, upvotes, image1, image2, image3):
        try: app.db.execute('''
INSERT INTO ProductReview VALUES (:user_id, :product_id, :seller_id, :num_stars, :date, :description, :upvotes, :images)
        ''', user_id=user_id, product_id=product_id, seller_id=seller_id, num_stars=num_stars, date=date, description=description, upvotes=upvotes, images=[image1, image2, image3])
        except Exception as e:
            print(e)

    @staticmethod
    ##Method to update a selected product review authored by user with user_id
    def update_product_review(user_id, product_id, seller_id, num_stars, date, description, upvotes, image1, image2, image3):
        try: app.db.execute('''
UPDATE ProductReview SET (num_stars, date, description, upvotes, images) = (:num_stars, :date, :description, :upvotes, :images)
WHERE buyer_id = :user_id AND product_id = :product_id AND seller_id = :seller_id
        ''', user_id=user_id, product_id=product_id, seller_id=seller_id, num_stars=num_stars, date=date, upvotes=upvotes, description=description, images=[image1, image2, image3])
        except Exception as e:
            print(e)

    @staticmethod
    ##Method to delete a selected product review authored by user with user_id
    def delete_product_review(user_id, product_id, seller_id):
        try: app.db.execute('''
DELETE FROM ProductReview WHERE buyer_id = :user_id AND product_id = :product_id AND seller_id = :seller_id
        ''', user_id=user_id, product_id=product_id, seller_id=seller_id)
        except Exception as e:
            print(e)

    @staticmethod
    ##Method to upvote a product review
    def upvote_product_review(user_id, product_id, seller_id, upvotes):
        try: app.db.execute('''
UPDATE ProductReview SET upvotes = :upvotes
WHERE buyer_id = :user_id AND product_id = :product_id AND seller_id = :seller_id
        ''', user_id=user_id, product_id=product_id, seller_id=seller_id, upvotes=str(int(upvotes)+1))
        
        except Exception as e:
            
            print(e)


class userSellerReview:
    def __init__(self, seller_id, fname, lname, num_stars, date, description, upvotes, images):
        self.seller_id = seller_id
        self.name = fname + ' ' + lname
        self.num_stars = num_stars
        self.date = date
        self.description = description
        self.upvotes = upvotes
        self.images = images

    @staticmethod
    ##method to get all seller reviews written by user with user_id in reverse chronological order
    def get(user_id):
        rows = app.db.execute('''
SELECT seller_id, firstname, lastname, num_stars, date, sr.description, upvotes, images
FROM SellerReview sr, Account a
WHERE sr.buyer_id = :user_id
AND a.account_id = sr.seller_id
ORDER BY date DESC
''',
                              user_id=user_id)
        return [userSellerReview(*row) for row in rows] if rows is not None else None

    @staticmethod
    ##Method to submit a seller review authored by user with user_id
    def submit_seller_review(user_id, seller_id, num_stars, date, description, upvotes, image1, image2, image3): 
        try: app.db.execute('''
INSERT INTO SellerReview VALUES (:user_id, :seller_id, :num_stars, :date, :description, :upvotes, :images)
        ''', user_id=user_id, seller_id=seller_id, num_stars=num_stars, date=date, description=description, upvotes=upvotes, images=[image1, image2, image3])
        except Exception as e:
            print(e)

    @staticmethod
    ##Method to update a selected seller review authored by user with user_id 
    def update_seller_review(user_id, seller_id, num_stars, date, description, upvotes, image1, image2, image3):
        try: app.db.execute('''
UPDATE SellerReview SET (num_stars, date, description, upvotes, images) = (:num_stars, :date, :description, :upvotes, :images)
WHERE buyer_id = :user_id AND seller_id = :seller_id
        ''', user_id=user_id, seller_id=seller_id, num_stars=num_stars, date=date, description=description, upvotes=upvotes, images=[image1, image2, image3])
        except Exception as e:
            print(e)

    @staticmethod
    ##Method to delete a selected seller review authored by user with user_id
    def delete_seller_review(user_id, seller_id):
        try: app.db.execute('''
DELETE FROM SellerReview WHERE buyer_id = :user_id AND seller_id = :seller_id
        ''', user_id=user_id, seller_id=seller_id)
        except Exception as e:
            print(e)

    @staticmethod
    ##Method to upvote a seller review
    def upvote_seller_review(user_id, seller_id, upvotes):
        try: app.db.execute('''
UPDATE SellerReview SET upvotes = :upvotes
WHERE buyer_id = :user_id AND seller_id = :seller_id
        ''', user_id=user_id, seller_id=seller_id, upvotes=str(int(upvotes)+1))
        except Exception as e:
            print(e)


 

