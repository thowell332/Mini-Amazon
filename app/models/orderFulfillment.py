from flask import current_app as app

class OrderHistory:
    def __init__(self, purchase_id, buyer_name, buyer_address, date, quantity, status):
        self.purchase_id = purchase_id
        self.buyer_name = buyer_name
        self.buyer_address = buyer_address
        self.date = date
        self.quantity = quantity
        self.status = status
    
    @staticmethod
    # retrieve seller order fulfillment history
    def get(seller_id):
        rows = app.db.execute(
            '''
            SELECT p.purchase_id, CONCAT(a.firstname,' ',a.lastname) as buyer_name,
            a.address, p.date, COUNT(p.item_id) as quantity, MIN(p.status) as status
            FROM Purchase p, Account a
            WHERE p.seller_id = :seller_id AND a.account_id = p.buyer_id
            GROUP BY p.purchase_id, a.firstname, a.lastname, a.address, p.date;
            ''',
            seller_id=seller_id
        )
        return [OrderHistory(*row) for row in rows] if rows is not None else None
    
    @staticmethod
    # retrieve individual order fulfillment details
    def get_order_fulfillment(purchase_id):
        row = app.db.execute(
            '''
            SELECT p.purchase_id, CONCAT(a.firstname,' ',a.lastname) as buyer_name,
            a.address, p.date, COUNT(p.item_id) as quantity, MIN(p.status) as status
            FROM Purchase p, Account a
            WHERE p.purchase_id = :purchase_id AND a.account_id = p.buyer_id
            GROUP BY p.purchase_id, a.firstname, a.lastname, a.address, p.date;
            ''',
            purchase_id=purchase_id
        )
        print(row[0])
        return OrderHistory(*(row[0])) if row else None

