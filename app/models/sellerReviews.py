from flask import current_app as app

        
class sellerReview:
    def __init__(self, buyer_id, seller_id, num_stars, date, description, upvotes, images):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.num_stars = num_stars
        self.date = date
        self.description = description
        self.upvotes = upvotes
        self.images = images

    @staticmethod
    ##method to get all reviews for a given seller in reverse chronological order
    def get(seller_id):
        rows = app.db.execute(
'''
SELECT buyer_id, seller_id, num_stars, date, description, upvotes, images FROM (SELECT buyer_id, seller_id, num_stars, date, description, upvotes, images
    FROM (SELECT buyer_id, seller_id, num_stars, date, description, upvotes, images
    FROM SellerReview
    WHERE seller_id = :seller_id
    ORDER BY upvotes DESC) AS sortedReviews
    LIMIT 3) AS topThree
UNION ALL
(SELECT buyer_id, seller_id, num_stars, date, description, upvotes, images FROM SellerReview
WHERE seller_id = :seller_id AND NOT EXISTS (
    SELECT buyer_id, seller_id, num_stars, date, description, upvotes, images FROM (SELECT buyer_id, seller_id, num_stars, date, description, upvotes, images
    FROM (SELECT buyer_id, seller_id, num_stars, date, description, upvotes, images
    FROM SellerReview
    WHERE seller_id = :seller_id
    ORDER BY upvotes DESC) AS sortedReviews
    LIMIT 3) AS topThree
    WHERE SellerReview.buyer_id = buyer_id
)
ORDER BY date DESC)
''',
                              seller_id=seller_id)
        return [sellerReview(*row) for row in rows] if rows is not None else None

