from app import app
from app.models import Cart
from flask import render_template
from flask_login import current_user, login_required


posts = [
    {
        'author': 'Amanda Stan',
        'title': 'Orange new Black',
    },
    {
        'author': 'Jane Carey',
        'title': 'Summer in the City',
    }
]


def cart_count():
    if current_user.is_authenticated:
        return Cart.query.filter_by(user_id=current_user.id).count()
    else:
        return 0


@app.route("/")
@app.route("/home")
def home():
    categories = ["Men", "Woman", "Kids"]
    return render_template("home.html", categories=categories, carts_count=cart_count())


@app.route("/about")
def about():
    return render_template("about.html", carts_count=cart_count(), title="About")


@app.route("/contact")
def contact():
    return render_template("contact.html", carts_count=cart_count(), title="Cart")


@app.route("/career")
def career():
    return render_template("career.html", carts_count=cart_count(), title="Cart")