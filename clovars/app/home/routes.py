from __future__ import annotations

from flask import render_template, redirect, url_for, request, Blueprint

from clovars.app.forms import NewTreatmentForm
from clovars.app.models import Treatment, db

# Blueprint Configuration
main_blueprint = Blueprint(
    'main_blueprint',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@main_blueprint.route("/")
@main_blueprint.route("/index")
def index() -> str:
    return render_template('index.html')


@main_blueprint.route("/about")
def about() -> str:
    return render_template('about.html')


@main_blueprint.route("/view_treatments")
def view_treatments() -> str:
    t = Treatment.query.all()
    return render_template('view_treatments.html', treatments=t)


@main_blueprint.route("/new_treatments", methods=['GET', 'POST'])
def new_treatment() -> str:
    treatment_form = NewTreatmentForm()
    if request.method == 'GET':
        return render_template('new_treatment.html', form=treatment_form)
    elif request.method == 'POST':
        if treatment_form.validate_on_submit():
            name = treatment_form.name.data
            new_t = Treatment(name=name)
            db.session.add(new_t)
            db.session.commit()
            return redirect(url_for('main_blueprint.view_treatments'))
        else:  # Form was invalid
            print("INVALID!")
            return render_template('new_treatment.html', form=treatment_form)
