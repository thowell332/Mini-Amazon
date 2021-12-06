from flask import Flask
from flask_login import LoginManager
from flask_babel import Babel
from flask import Flask
from flask_login import LoginManager
from flask_babel import Babel
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'
babel = Babel()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)
    babel.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .cart import bp as cart_bp
    app.register_blueprint(cart_bp)

    from .inventories import bp as inventory_bp
    app.register_blueprint(inventory_bp)

    from .product import bp as product_bp
    app.register_blueprint(product_bp)

    from .productSearchInput import bp as productSearchInput_bp
    app.register_blueprint(productSearchInput_bp)

    from .productSearchCategory import bp as productSearchCategory_bp
    app.register_blueprint(productSearchCategory_bp)

    from .newProduct import bp as newProduct_bp
    app.register_blueprint(newProduct_bp)

    from .cart import bp as cart_bp
    app.register_blueprint(cart_bp)

    return app
