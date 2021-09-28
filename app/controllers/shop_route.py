import secrets
import os
from PIL import Image
from app import app, db
from flask import render_template, url_for, flash, redirect, request
from flask_login import current_user, login_required
from app.models import Products, Cart
from app.forms import UpdateItemForm
from sqlalchemy import select


def cart_count():
    if current_user.is_authenticated:
        return Cart.query.filter_by(user_id=current_user.id).count()
    else:
        return 0


@app.route("/cart", methods=['GET', 'POST'])
@login_required
def cart():
    id = current_user.id
    carts = Cart.query.filter_by(user_id=id).all()
    products_id = _get_products_id(carts)
    results = []

    for product_id in products_id:
        products = Products.query.filter_by(product_id=product_id).first()
        results.append(products)

    total_price = _calculate_total_price(results)
    return render_template("cart.html", products=results, total_price=total_price, carts_count=cart_count(),
                           title="Carts")


@app.route("/catalog", methods=['GET', 'POST'])
def catalog():
    categories = ["Men", "Woman", "Kids"]
    return render_template("catalog.html", categories=categories, carts_count=cart_count(), title="Product Catalog")


@app.route("/category")
def category():
    category_name = request.url.split('=')[1]
    products = Products.query.filter_by(category=category_name).all()
    return render_template('category.html', products=products, category_name=category_name, carts_count=cart_count(),
                           title="Display Category")


@app.route("/checkout")
@login_required
def checkout():
    db.session.query(Cart).delete()
    db.session.commit()
    flash("Your purchases have been completed", "success")
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "views/static/shoes", picture_name)

    output_size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_name


@app.route('/item/new', methods=['POST', 'GET'])
@login_required
def new_item():
    form = UpdateItemForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)
        print(f"size!!!  {form.size.data}")

        product = Products(
            name=form.name.data,
            price=form.price.data,
            category=form.category.data,
            size=form.size.data,
            description=form.description.data,
            image_file=picture_file
        )
        db.session.add(product)
        db.session.commit()
        flash("New item is added", "success")
        return redirect(url_for("home"))
    return render_template('create_item.html', form=form, carts_count=cart_count(), title="New Item")


@app.route("/products", methods=['GET'])
def get_all_products():
    products = Products.query.all()
    return _map_response(products)


def _map_response(data):
    products = {}
    for product in data:
        products[product.product_id] = {
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "category": product.category,
            "image": product.image_file
        }
    return products


@app.route("/product_description", methods=['GET', 'POST'])
def product_description():
    product_id = request.url.split("=")[1]
    product = Products.query.filter_by(product_id=product_id).first()
    return render_template("product_description.html", product=product, carts_count=cart_count(),
                           title="Product Description")


@app.route("/add_to_cart")
@login_required
def add_to_cart():
    product_id = request.url.split("=")[1]
    user_id = current_user.id
    cart = Cart(
        user_id=user_id,
        product_id=product_id
    )
    db.session.add(cart)
    db.session.commit()

    return redirect(url_for('home'))


@app.route("/remove_from_cart")
@login_required
def remove_from_cart():
    product_id = request.url.split("=")[1]
    user_id = current_user.id
    print(f"product id {product_id}")
    print(f"user id {user_id}")
    product = Cart.query.filter_by(product_id=product_id, user_id=user_id).first()
    print(f"product {product}")
    db.session.delete(product)
    db.session.commit()
    flash("Your cart has been updated", "success")

    return redirect(url_for('home'))


def _get_products_id(data):
    product_ids = []
    for product in data:
        product_ids.append(product.product_id)
    return tuple(product_ids)


def _map_producst(data):
    products = {}
    for product in data:
        products[product.product_id] = {
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "category": product.category,
            "image": product.image_file
        }
    return products


def _calculate_total_price(products):
    total_price = 0
    for product in products:
        total_price += product.price
    return total_price


def _cart_product(data):
    carts = {}
    for product in data:
        carts[product.id] = {
            "user_id": product.user_id,
            "product_id": product.product_id
        }
    return carts
