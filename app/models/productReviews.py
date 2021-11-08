from flask import current_app as app

class productReviewSummary:
    def __init__(self, count, average):
        self.count = count
        self.average = average

    @staticmethod
    ##method to get number of and average of reviews for a given product
    def get(product_id):
        row = app.db.execute('''
SELECT COUNT(*), AVG(num_stars)
FROM ProductReview
WHERE product_id = :product_id
''',
                              product_id=product_id)
        return productReviewSummary(*(row[0])) if row is not None else None

        
class productReview:
    def __init__(self, buyer_id, num_stars, date, description):
        self.buyer_id = buyer_id
        self.num_stars = num_stars
        self.date = date
        self.description = description

    @staticmethod
    ##method to get all reviews for a given product in reverse chronological order
    def get(product_id):
        rows = app.db.execute('''
SELECT buyer_id, num_stars, date, description
FROM ProductReview
WHERE product_id = :product_id
ORDER BY date DESC
''',
                              product_id=product_id)
        return [productReview(*row) for row in rows] if rows is not None else None
