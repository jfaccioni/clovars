from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, TreatmentRegimen, Schedule, Treatment, Curve


class DBManager:
    """Class responsible for managing the connection to the database."""
    def __init__(
            self,
    ) -> None:
        """Initializes a DBManager instance."""
        self.engine = None

    @contextmanager
    def get_session(self) -> Iterator[Session, None, None]:
        """Context manager for opening a session and returning it."""
        if self.engine is None:
            raise ValueError("Cannot get session if engine is set to None.")
        with Session(self.engine) as session:
            yield session
            session.commit()

    def connect_db(
            self,
            dialect: str = 'sqlite',
            driver: str = 'pysqlite',
            url: str = '/:memory:',
            echo: bool = True,
    ) -> None:
        """Sets up the connection to the database."""
        path = f"{dialect}{'+' + driver if driver else ''}://{url}"
        self.engine = create_engine(path, echo=echo, future=True)
        Base.metadata.create_all(self.engine)


if __name__ == '__main__':
    db_manager = DBManager()
    db_manager.connect_db(echo=False)

    with db_manager.get_session() as session:
        schedules = [
            Schedule(frame=0, treatment=Treatment(
                name='Control',
                division_curve=Curve(name='Control_div', type='Gaussian', mean=24.0, std=3.0),
                death_curve=Curve(name='Control_dth', type='Gaussian', mean=34.0, std=3.0),
            )),
            Schedule(frame=72, treatment=Treatment(
                name='TMZ',
                division_curve=Curve(name='TMZ_div', mean=24.0, std=3.0),
                death_curve=Curve(name='TMZ_dth', mean=25.0, std=3.0),
            )),
        ]
        # regimen = TreatmentRegimen(name='MyTreatmentRegimen', schedules=schedules)
        regimen = TreatmentRegimen(name='MyTreatmentRegimen')
        session.add(regimen)
    with db_manager.get_session() as session:
        records = session.query(TreatmentRegimen).all()
        for regimen in records:
            print(regimen)
