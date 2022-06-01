from __future__ import annotations

from typing import TYPE_CHECKING

from clovars.app import db

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy


class TreatmentRegimen(db.Model):
    __tablename__ = 'treatment_regimen'
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String)

    # RELATIONSHIP WITH SCHEDULE - MANY TreatmentRegimens TO ONE Schedule
    schedules: list[Schedule] = db.relationship(
        "Schedule",
        back_populates="treatment_regimen",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        """Returns a string representation of the TreatmentRegimen."""
        return f"TreatmentRegimen(id={self.id}, name={self.name}, schedules={self.schedules})"

    def __repr__(self) -> str:
        """Returns a programmatic representation of the TreatmentRegimen."""
        return str(self)


class Schedule(db.Model):
    __tablename__ = 'schedule'
    id: int = db.Column(db.Integer, primary_key=True)
    frame: int = db.Column(db.Integer)

    # RELATIONSHIP WITH TREATMENT REGIMEN - ONE Schedule TO MANY TreatmentRegimens
    treatment_regimen_id: int = db.Column(db.Integer, db.ForeignKey("treatment_regimen.id"))
    treatment_regimen: TreatmentRegimen = db.relationship("TreatmentRegimen", back_populates="schedules")

    # RELATIONSHIP WITH TREATMENT - ONE Schedule TO MANY Treatments
    treatment_id: int = db.Column(db.Integer, db.ForeignKey("treatment.id"))
    treatment: Treatment = db.relationship("Treatment")

    def __str__(self) -> str:
        """Returns a string representation of the Schedule."""
        return f"Schedule(id={self.id}, frame={self.frame}, treatment={self.treatment})"

    def __repr__(self) -> str:
        """Returns a programmatic representation of the Schedule."""
        return str(self)


class Treatment(db.Model):
    __tablename__ = 'treatment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # RELATIONSHIP WITH DIVISION CURVE - ONE Treatment TO MANY Curves
    division_curve_id: int = db.Column(db.Integer, db.ForeignKey("curve.id"))
    division_curve: Curve = db.relationship("Curve", foreign_keys=[division_curve_id])

    # RELATIONSHIP WITH DEATH CURVE - ONE Treatment TO MANY Curves
    death_curve_id: int = db.Column(db.Integer, db.ForeignKey("curve.id"))
    death_curve: Curve = db.relationship("Curve", foreign_keys=[death_curve_id])

    def __str__(self) -> str:
        """Returns a string representation of the Treatment."""
        return f"Treatment(id={self.id}, name={self.name}, division_curve={self.division_curve}, death_curve={self.death_curve})"

    def __repr__(self) -> str:
        """Returns a programmatic representation of the Treatment."""
        return str(self)


class Curve(db.Model):
    __tablename__ = 'curve'
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String)
    type: str = db.Column(db.String)
    mean: float = db.Column(db.Float)
    std: float = db.Column(db.Float)
    k: float = db.Column(db.Float)
    a: float = db.Column(db.Float)
    s: float = db.Column(db.Float)

    def __str__(self) -> str:
        """Returns a string representation of the Curve."""
        return f"Curve(id={self.id}, name={self.name}, type={self.type}, mean={self.mean}, std={self.std} k={self.k}, a={self.a}, s={self.s})"

    def __repr__(self) -> str:
        """Returns a programmatic representation of the Curve."""
        return str(self)


def place_initial_data(database: SQLAlchemy) -> None:
    """Sets up the initial data on the database."""
    regimen = TreatmentRegimen(
        name='MyTreatmentRegimen',
        schedules=[
            Schedule(
                frame=0,
                treatment=Treatment(
                    name='Control',
                    division_curve=Curve(
                        name='Control_div',
                        type='Gaussian',
                        mean=24.0,
                        std=3.0,
                    ),
                    death_curve=Curve(
                        name='Control_dth',
                        type='Gaussian',
                        mean=34.0,
                        std=3.0,
                    ),
                ),
            ),
            Schedule(
                frame=72,
                treatment=Treatment(
                    name='TMZ',
                    division_curve=Curve(
                        name='TMZ_div',
                        mean=24.0,
                        std=3.0,
                    ),
                    death_curve=Curve(
                        name='TMZ_dth',
                        mean=25.0,
                        std=3.0,
                    ),
                ),
            ),
        ]
    )
    database.session.add(regimen)
    database.session.commit()
