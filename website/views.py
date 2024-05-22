from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user


views_blueprint = Blueprint('views_blueprint', __name__)


@views_blueprint.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)
