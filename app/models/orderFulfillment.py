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
            GROUP BY p.purchase_id, a.firstname, a.lastname, a.address, p.date
            ORDER BY p.date DESC;
            ''',
            seller_id=seller_id
        )
        return [OrderHistory(*row) for row in rows] if rows is not None else None
    
    @staticmethod
    # retrieve search results for seller order fulfillment history
    def get_search_results(seller_id, search_field, search_criteria):
        search_criteria = "%" + search_criteria.replace(" ", "%") + "%"
        if search_field == 'buyer_name':
            rows = app.db.execute(
                '''
                SELECT pu.purchase_id, CONCAT(a.firstname,' ',a.lastname) as buyer_name,
                a.address, pu.date, COUNT(pu.item_id) as quantity, MIN(pu.status) as status
                FROM Purchase pu, Account a
                WHERE pu.seller_id = :seller_id AND a.account_id = pu.buyer_id
                AND (a.firstname ILIKE :search_criteria OR a.lastname ILIKE :search_criteria)
                GROUP BY pu.purchase_id, a.firstname, a.lastname, a.address, pu.date
                ORDER BY pu.date DESC;
                ''',
                seller_id=seller_id,
                search_criteria=search_criteria
            )
        elif search_field == "buyer_address":
            rows = app.db.execute(
                '''
                SELECT pu.purchase_id, CONCAT(a.firstname,' ',a.lastname) as buyer_name,
                a.address, pu.date, COUNT(pu.item_id) as quantity, MIN(pu.status) as status
                FROM Purchase pu, Account a
                WHERE pu.seller_id = :seller_id AND a.account_id = pu.buyer_id
                AND a.address ILIKE :search_criteria
                GROUP BY pu.purchase_id, a.firstname, a.lastname, a.address, pu.date
                ORDER BY pu.date DESC;
                ''',
                seller_id=seller_id,
                search_criteria=search_criteria
            )
        elif search_field == "product_name":
            rows = app.db.execute(
                '''
                SELECT pu.purchase_id, CONCAT(a.firstname,' ',a.lastname) as buyer_name,
                a.address, pu.date, COUNT(pu.item_id) as quantity, MIN(pu.status) as status
                FROM Purchase pu, Account a, Product pr
                WHERE pu.seller_id = :seller_id AND a.account_id = pu.buyer_id
                AND pr.product_id = pu.product_id AND pr.name ILIKE :search_criteria
                GROUP BY pu.purchase_id, a.firstname, a.lastname, a.address, pu.date
                ORDER BY pu.date DESC;
                ''',
                seller_id=seller_id,
                search_criteria=search_criteria
            )
        else:
            rows = app.db.execute(
                '''
                SELECT pu.purchase_id, CONCAT(a.firstname,' ',a.lastname) as buyer_name,
                a.address, pu.date, COUNT(pu.item_id) as quantity, MIN(pu.status) as status
                FROM Purchase pu, Account a, Product pr
                WHERE pu.seller_id = :seller_id AND a.account_id = pu.buyer_id
                AND pr.product_id = pu.product_id AND pr.description ILIKE :search_criteria
                GROUP BY pu.purchase_id, a.firstname, a.lastname, a.address, pu.date
                ORDER BY pu.date DESC;
                ''',
                seller_id=seller_id,
                search_criteria=search_criteria
            )
        return [OrderHistory(*row) for row in rows] if rows is not None else None
    
    @staticmethod
    # retrieve individual order fulfillment details
    def get_purchase(seller_id, purchase_id):
        row = app.db.execute(
            '''
            SELECT p.purchase_id, CONCAT(a.firstname,' ',a.lastname) as buyer_name,
            a.address, p.date, COUNT(p.item_id) as quantity, MIN(p.status) as status
            FROM Purchase p, Account a
            WHERE p.purchase_id = :purchase_id AND a.account_id = p.buyer_id
            AND p.seller_id = :seller_id
            GROUP BY p.purchase_id, a.firstname, a.lastname, a.address, p.date;
            ''',
            purchase_id=purchase_id,
            seller_id=seller_id
        )
        return OrderHistory(*(row[0])) if row else None


class OrderFulfillment:
    def __init__(self, product_id, product_name, product_description, quantity, status):
        self.product_id = product_id
        self.product_name = product_name
        self.product_description = product_description
        self.quantity = quantity
        self.status = status
    
    @staticmethod
    # retrieve individual order fulfillment details
    def get_order_fulfillment(seller_id, purchase_id):
        rows = app.db.execute(
            '''
            SELECT pr.product_id, pr.name as product_name, pr.description as product_description,
            COUNT(pu.item_id) as quantity, MIN(pu.status) as status
            FROM Purchase pu, Product pr
            WHERE pu.purchase_id = :purchase_id AND pr.product_id = pu.product_id
            AND pu.seller_id = :seller_id
            GROUP BY pr.product_id, pr.name, pr.description;
            ''',
            purchase_id=purchase_id,
            seller_id=seller_id
        )
        return [OrderFulfillment(*row) for row in rows] if rows is not None else None


class ItemFulfillment:
    def __init__(self, item_id, status):
        self.item_id = item_id
        self.status = status
    
    @staticmethod
    # retrieve individual item fulfillment details
    def get_item_fulfillment(seller_id, purchase_id, product_id):
        rows = app.db.execute(
            '''
            SELECT p.item_id, p.status
            FROM Purchase p
            WHERE p.purchase_id = :purchase_id AND p.product_id = :product_id
            AND p.seller_id = :seller_id;
            ''',
            purchase_id=purchase_id,
            product_id=product_id,
            seller_id=seller_id
        )
        return [ItemFulfillment(*row) for row in rows] if rows is not None else None
    
    @staticmethod
    # update statuses
    def update_status(seller_id, purchase_id, product_id, item_id, status):
        print(item_id)
        print(status)
        # update the statuses of all items of same product if item_id = -1
        if item_id == -1:
            try: app.db.execute(
                '''
                UPDATE Purchase SET status = :status
                WHERE purchase_id = :purchase_id AND product_id = :product_id
                AND seller_id = :seller_id;
                ''',
                purchase_id=purchase_id,
                product_id=product_id,
                status=status,
                seller_id=seller_id
            )
            except Exception as e:
                print(e)
        # else update status of individual item
        else:
            try: app.db.execute(
                '''
                UPDATE Purchase SET status = :status
                WHERE purchase_id = :purchase_id AND product_id = :product_id
                AND item_id = :item_id AND seller_id = :seller_id;
                ''',
                purchase_id=purchase_id,
                product_id=product_id,
                item_id=item_id,
                status=status,
                seller_id=seller_id
            )
            except Exception as e:
                print(e)
