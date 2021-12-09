from flask import current_app as app

        
class productReview:
    def __init__(self, buyer_id, product_id, seller_id, num_stars, date, description, upvotes, images):
        self.buyer_id = buyer_id
        self.product_id = product_id
        self.seller_id = seller_id
        self.num_stars = num_stars
        self.date = date
        self.description = description
        self.upvotes = upvotes
        self.images = images

    @staticmethod
    ##method to get all reviews for a given product in reverse chronological order with top three upvoted reviews listed first
    def get(product_id, seller_id):
        rows = app.db.execute('''

SELECT buyer_id, product_id, seller_id, num_stars, date, description, upvotes, images FROM (SELECT buyer_id, product_id, seller_id, num_stars, date, description, upvotes, images
    FROM (SELECT buyer_id, product_id, seller_id, num_stars, date, description, upvotes, images
    FROM ProductReview
    WHERE product_id = :product_id AND seller_id = :seller_id
    ORDER BY upvotes DESC) AS sortedReviews
    LIMIT 3) AS topThree
UNION ALL
(SELECT buyer_id, product_id, seller_id, num_stars, date, description, upvotes, images FROM ProductReview
WHERE product_id = :product_id AND NOT EXISTS (
    SELECT buyer_id, product_id, seller_id, num_stars, date, description, upvotes, images FROM (SELECT buyer_id, product_id, seller_id, num_stars, date, description, upvotes, images
    FROM (SELECT buyer_id, product_id, seller_id, num_stars, date, description, upvotes, images
    FROM ProductReview
    WHERE product_id = :product_id AND seller_id = :seller_id
    ORDER BY upvotes DESC) AS sortedReviews
    LIMIT 3) as topThree
    WHERE ProductReview.buyer_id = buyer_id
)
ORDER BY date DESC)
'''
,
                              product_id=product_id, seller_id=seller_id)
        return [productReview(*row) for row in rows] if rows is not None else None

