from ctypes import addressof
from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login

#create user class
class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.balance = balance

    #checks the user entered a valid (email, password) combo
    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""SELECT * FROM Account WHERE email = :email""", email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][-1], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][:-1]))

    #determine whether email exists in the Account table
    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Account
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    #insert new user into Account table
    @staticmethod
    def register(email, password, firstname, lastname, address):
        try:
            rows = app.db.execute("""
INSERT INTO Account(email, password, firstname, lastname, address, balance)
VALUES(:email, :password, :firstname, :lastname, :address, 0.00)
RETURNING account_id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname,
                                  lastname=lastname,
                                  address=address)
            id = rows[0][0]
            return User.get(id)
        except Exception:
            # likely email already in use; better error checking and
            # reporting needed
            return None

    #get a user's information when given an account_id
    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
            SELECT account_id, email, firstname, lastname, address, balance
            FROM Account
            WHERE account_id = :id
            """,
            id=id)
        return User(*(rows[0])) if rows else None

    #update user's information in Account
    @staticmethod
    def updateProfile(id, email, firstname, lastname, address):
        rows = app.db.execute("""
            UPDATE Account
            SET account_id = :id, email = :email, firstname = :firstname, lastname = :lastname, address = :address
            WHERE account_id = :id
            RETURNING account_id""", 
            id=id, email=email, firstname=firstname, lastname=lastname, address=address)
        return 1 if rows else None
    
    #update a user's password in Account table
    @staticmethod
    def updatePassword(id, password):
        app.db.execute("""
            UPDATE Account
            SET password = :password
            WHERE account_id = :id
            RETURNING account_id""", 
            id=id, password=generate_password_hash(password))
        return 1
            
    #update a User's balance
    def update_balance(account_id, new_balance):
        app.db.execute("""
            UPDATE Account
            SET balance = :new_balance
            WHERE account_id = :account_id
            RETURNING 1""",
            account_id = account_id, new_balance = new_balance)

    #get a user's balance
    @staticmethod
    def get_balance(account_id):
        rows = app.db.execute(
            """
            SELECT balance
            FROM Account
            WHERE account_id = :account_id
            """,
            account_id = account_id)
        return rows[0][0]

    #get a user's Seller Status
    @staticmethod
    def sellerStatus(account_id):
        rows = app.db.execute("""
        SELECT *
        FROM Seller
        WHERE seller_id = :account_id""",
        account_id = account_id)
        if rows:
            return 1
        else:
            return 0
    
    #insert account_id into Seller table
    @staticmethod
    def becomeSeller(account_id):
        try:
            rows = app.db.execute("""
            INSERT INTO Seller(seller_id)
            VALUES(:account_id)
            RETURNING :account_id""",
            account_id=account_id)
            return account_id
        except Exception:
            #already a seller
            return
#class for user's public view
#public view for non-sellers includes id, firstname, lastname
#public view for sellers includes above, plus email and addresss
class UserView:
    def __init__(self, id, firstname, lastname, email, address):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.address = address

    #get regular users' id and name, join with sellers' email and address
    @staticmethod
    def getUsersPublicView():
        rows = app.db.execute("""
        WITH q1 AS (SELECT account_id, firstname, lastname FROM Account),
        q2 AS (SELECT account_id, email, address FROM Account
        WHERE account_id IN (SELECT seller_id FROM Seller))
        SELECT q1.account_id, q1.firstname, q1.lastname, q2.email, q2.address FROM q1 LEFT OUTER JOIN q2 ON q1.account_id = q2.account_id""")
        return [UserView(*row) for row in rows]
