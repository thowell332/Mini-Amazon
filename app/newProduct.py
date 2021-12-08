from flask import render_template, redirect, url_for, flash, current_app as app, request
from flask_login import current_user

from .models.product import Product
from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_babel import _, lazy_gettext as _l

from .models.user import User

bp = Blueprint('newProduct', __name__)

class NewProductForm(FlaskForm):
    owner_id = StringField(_l('Owner ID'), validators=[DataRequired()])
    product_name = StringField(_l('Product Name'), validators=[DataRequired()])
    product_description = StringField(_l('Product Description'), validators=[DataRequired()])
    product_image = StringField(_l('Product Image'), validators=[DataRequired()])
    product_category = StringField(_l('Product Category'), validators=[DataRequired()])
    submit = SubmitField(_l('Add New Product'))

class editProductForm(FlaskForm):
    product_name = StringField(_l('New Product Name:'), validators=[DataRequired()])
    product_description = StringField(_l('New Product Description:'), validators=[DataRequired()])
    product_image = StringField(_l('New Product Image:'), validators=[DataRequired()])
    product_category = StringField(_l('New Product Category:'), validators=[DataRequired()])
    submit = SubmitField(_l('Update Product'))


# Method to add a new product.  Takes in a user input of all the necessary product
# information and adds it to the database.
@bp.route('/newProduct', methods=['GET', 'POST'])
def addNewProduct():
    # redirect to login if not authenticated
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    
    # redirect to homepage if not seller
    seller_status = User.sellerStatus(current_user.id)
    if seller_status != 1:
        return redirect(url_for('index.index'))
    
    # build new product form
    form = NewProductForm()
    if form.validate_on_submit():
        if Product.insert_new_product(form.owner_id.data,
                                      form.product_description.data,
                                      form.product_name.data,
                                      form.product_image.data,
                                      form.product_category.data):
            return redirect(url_for('inventories.inventory'))
    return render_template('newProduct.html', title='Add New Product', form=form, seller_status=seller_status)

# Method to edit a product.  Takes in a user input of all the updatable information and updates the record in the database.
# @param input- the product id of the product being updated.
@bp.route('/editProduct<input>', methods=['GET', 'POST'])
def editProduct(input):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    form = editProductForm()
    current_product = Product.get(input)
    if form.validate_on_submit():
        if Product.update_product(input, form.product_description.data, form.product_name.data, form.product_image.data, form.product_category.data):
            return redirect(url_for('inventories.inventory'))
    return render_template('editProduct.html', title='Edit Product', form=form, current_product=current_product)




