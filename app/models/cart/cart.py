from flask import current_app as app

class Cart():
    def __init__(self, user_id, email, firstname, lastname):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname)
VALUES(:email, :password, :firstname, :lastname)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname,
                                  lastname=lastname)
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
SELECT id, email, firstname, lastname
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None
