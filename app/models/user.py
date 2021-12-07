from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""SELECT * FROM Account WHERE email = :email""", email=email)
        print(rows[0])
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][-1], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][:-1]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Account
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

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

    @staticmethod
    def update_balance(account_id, new_balance):
        app.db.execute(
"""
UPDATE Account
SET balance = :new_balance
WHERE account_id = :account_id
RETURNING 1
""",
        account_id = account_id, new_balance = new_balance)

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