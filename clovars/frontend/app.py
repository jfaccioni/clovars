from __future__ import annotations

import os

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from clovars import ROOT_PATH
from clovars.frontend.models.models import db, Treatment

DEV = True

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{ROOT_PATH / "clovars" / "frontend" / "test.db"}'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')  # Remember to set SECRET_KEY env in production
Bootstrap(app)  # Flask-Bootstrap4 requires this line

db.init_app(app)

with app.app_context():
    if DEV is True:
        db.drop_all()  # Refreshes database during tests
    db.create_all()


class TreatmentForm(FlaskForm):
    name = StringField('Treatment name:', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/")
def index() -> str:
    return render_template('index.html')


@app.route("/about")
def about() -> str:
    return render_template('about.html')


@app.route("/view_treatments")
def view_treatments() -> str:
    t = Treatment.query.all()
    return render_template('view_treatments.html', treatments=t)


@app.route("/new_treatments", methods=['GET', 'POST'])
def new_treatment() -> str:
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    treatment_form = TreatmentForm()
    if treatment_form.validate_on_submit():  # POST
        name = treatment_form.name.data
        new_t = Treatment(name=name)
        db.session.add(new_t)
        db.session.commit()
        return redirect(url_for('view_treatments'))
    else:  # GET
        return render_template('new_treatment.html', form=treatment_form)
