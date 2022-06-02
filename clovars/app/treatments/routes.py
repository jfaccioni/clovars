from __future__ import annotations

from flask import render_template, redirect, url_for, request, Blueprint, Response

from clovars.app.forms import NewTreatmentForm
from clovars.app.models import Treatment, db

treatment_bp = Blueprint(
    'treatment_bp',
    __name__,
    url_prefix='/treatment',
    template_folder='templates',
    static_folder='static',
)


@treatment_bp.route("/view")
def view_treatments() -> str:
    treatments = Treatment.query.all()
    return render_template('view_treatments.html', treatments=treatments)


@treatment_bp.route("/new", methods=['GET', 'POST'])
def new_treatment() -> str | Response:
    treatment_form = NewTreatmentForm()
    if request.method == 'GET':
        return render_template('new_treatment.html', form=treatment_form)
    elif request.method == 'POST':
        if treatment_form.validate_on_submit():
            name = treatment_form.name.data
            new_treat = Treatment(name=name)
            db.session.add(new_treat)
            db.session.commit()
            return redirect(url_for('treatment_bp.view_treatments'))
        else:  # Form was invalid
            print("INVALID!")
            return render_template('new_treatment.html', form=treatment_form)
