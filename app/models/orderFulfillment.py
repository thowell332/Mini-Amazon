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
        search_criteria = "'%" + search_criteria + "%'"
        if search_field == 'buyer_name':
            search = 'a.firstname ILIKE ' + search_criteria + ' OR a.lastname ILIKE ' + search_criteria
        else:
            search = search_field + ' ILIKE ' + search_criteria
        rows = app.db.execute(
            '''
            SELECT pu.purchase_id, CONCAT(a.firstname,' ',a.lastname) as buyer_name,
            a.address, pu.date, COUNT(pu.item_id) as quantity, MIN(pu.status) as status
            FROM Purchase pu, Account a, Product pr
            WHERE pu.seller_id = :seller_id AND a.account_id = pu.buyer_id
            AND pr.product_id = pu.product_id AND 
            ''' + search +
            '''
            GROUP BY pu.purchase_id, a.firstname, a.lastname, a.address, pu.date
            ORDER BY p.date DESC;
            ''',
            seller_id=seller_id,
            search=search
        )
        return [OrderHistory(*row) for row in rows] if rows is not None else None
    
    @staticmethod
    # retrieve individual order fulfillment details
    def get_purchase(purchase_id):
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
    def get_order_fulfillment(purchase_id):
        rows = app.db.execute(
            '''
            SELECT pr.product_id, pr.name as product_name, pr.description as product_description,
            COUNT(pu.item_id) as quantity, MIN(pu.status) as status
            FROM Purchase pu, Product pr
            WHERE pu.purchase_id = :purchase_id AND pr.product_id = pu.product_id
            GROUP BY pr.product_id, pr.name, pr.description;
            ''',
            purchase_id=purchase_id
        )
        return [OrderFulfillment(*row) for row in rows] if rows is not None else None


class ItemFulfillment:
    def __init__(self, item_id, status):
        self.item_id = item_id
        self.status = status
    
    @staticmethod
    # retrieve individual item fulfillment details
    def get_item_fulfillment(purchase_id, product_id):
        rows = app.db.execute(
            '''
            SELECT p.item_id, p.status
            FROM Purchase p
            WHERE p.purchase_id = :purchase_id AND p.product_id = :product_id;
            ''',
            purchase_id=purchase_id,
            product_id=product_id
        )
        return [ItemFulfillment(*row) for row in rows] if rows is not None else None
    
    @staticmethod
    # update statuses
    def update_status(purchase_id, product_id, item_id, status):
        print(item_id)
        print(status)
        # update the statuses of all items of same product if item_id = -1
        if item_id == -1:
            try: app.db.execute(
                '''
                UPDATE Purchase SET status = :status
                WHERE purchase_id = :purchase_id AND product_id = :product_id;
                ''',
                purchase_id=purchase_id,
                product_id=product_id,
                status=status
            )
            except Exception as e:
                print(e)
        # else update status of individual item
        else:
            try: app.db.execute(
                '''
                UPDATE Purchase SET status = :status
                WHERE item_id = :item_id;
                ''',
                item_id=item_id,
                status=status
            )
            except Exception as e:
                print(e)
