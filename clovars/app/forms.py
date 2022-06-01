from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NewTreatmentForm(FlaskForm):
    """Form used to submit a new Treatment."""
    name = StringField('Treatment name:', validators=[DataRequired()])
    submit = SubmitField('Submit')
