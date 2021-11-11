from flask import render_template, redirect, url_for, flash, current_app as app

from .models.product import Product
from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_babel import _, lazy_gettext as _l

bp = Blueprint('newProduct', __name__)

class NewProductForm(FlaskForm):
    product_id = StringField(_l('Product ID'), validators=[DataRequired()])
    owner_id = StringField(_l('Owner ID'), validators=[DataRequired()])
    product_name = StringField(_l('Product Name'), validators=[DataRequired()])
    product_description = StringField(_l('Product Description'), validators=[DataRequired()])
    product_image = StringField(_l('Product Image'), validators=[DataRequired()])
    product_category = StringField(_l('Product Category'), validators=[DataRequired()])
    submit = SubmitField(_l('Add Product'))


@bp.route('/newProduct', methods=['GET', 'POST'])
def addNewProduct():
    form = NewProductForm()
    if form.validate_on_submit():
        if Product.insert_new_product(form.product_id.data,
                                      form.owner_id.data,
                                      form.product_description.data,
                                      form.product_name.data,
                                      form.product_image.data,
                                      form.product_category.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('index.index'))
    return render_template('newProduct.html', title='Add New Product', form=form)


