from __future__ import annotations

from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TreatmentRegimen(Base):
    __tablename__ = 'treatment_regimen'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)

    # RELATIONSHIP WITH SCHEDULE - MANY TreatmentRegimens TO ONE Schedule
    schedules: list[Schedule] = relationship(
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


class Schedule(Base):
    __tablename__ = 'schedule'
    id: int = Column(Integer, primary_key=True)
    frame: int = Column(Integer)

    # RELATIONSHIP WITH TREATMENT REGIMEN - ONE Schedule TO MANY TreatmentRegimens
    treatment_regimen_id: int = Column(Integer, ForeignKey("treatment_regimen.id"))
    treatment_regimen: TreatmentRegimen = relationship("TreatmentRegimen", back_populates="schedules")

    # RELATIONSHIP WITH TREATMENT - ONE Schedule TO MANY Treatments
    treatment_id: int = Column(Integer, ForeignKey("treatment.id"))
    treatment: Treatment = relationship("Treatment")

    def __str__(self) -> str:
        """Returns a string representation of the Schedule."""
        return f"Schedule(id={self.id}, frame={self.frame}, treatment={self.treatment})"

    def __repr__(self) -> str:
        """Returns a programmatic representation of the Schedule."""
        return str(self)


class Treatment(Base):
    __tablename__ = 'treatment'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # RELATIONSHIP WITH DIVISION CURVE - ONE Treatment TO MANY Curves
    division_curve_id: int = Column(Integer, ForeignKey("curve.id"))
    division_curve: Curve = relationship("Curve", foreign_keys=[division_curve_id])

    # RELATIONSHIP WITH DEATH CURVE - ONE Treatment TO MANY Curves
    death_curve_id: int = Column(Integer, ForeignKey("curve.id"))
    death_curve: Curve = relationship("Curve", foreign_keys=[death_curve_id])

    def __str__(self) -> str:
        """Returns a string representation of the Treatment."""
        return f"Treatment(id={self.id}, name={self.name}, division_curve={self.division_curve}, death_curve={self.death_curve})"

    def __repr__(self) -> str:
        """Returns a programmatic representation of the Treatment."""
        return str(self)


class Curve(Base):
    __tablename__ = 'curve'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    type: str = Column(String)
    mean: float = Column(Float)
    std: float = Column(Float)
    k: float = Column(Float)
    a: float = Column(Float)
    s: float = Column(Float)

    def __str__(self) -> str:
        """Returns a string representation of the Curve."""
        return f"Curve(id={self.id}, name={self.name}, type={self.type}, mean={self.mean}, std={self.std} k={self.k}, a={self.a}, s={self.s})"

    def __repr__(self) -> str:
        """Returns a programmatic representation of the Curve."""
        return str(self)
