from __future__ import annotations

from flask import render_template, Blueprint

home_bp = Blueprint(
    'home_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@home_bp.route("/")
@home_bp.route("/index")
@home_bp.route("/home")
def index() -> str:
    return render_template('index.html')


@home_bp.route("/about")
def about() -> str:
    return render_template('about.html')
