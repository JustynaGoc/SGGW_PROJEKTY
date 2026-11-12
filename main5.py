# ============================================================
# ============================================================

#Zadanie 5

# ============================================================
# ============================================================

import random
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String, create_engine, delete, func, select, update, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker, relationship


class Base(DeclarativeBase):
    pass


engine = create_engine("sqlite:///experiments.db", echo=True)

experiment_subject = Table(
    "experiment_subject",
    Base.metadata,
    Column("experiment_id", ForeignKey("experiment.id"), primary_key=True),
    Column("subject_id", ForeignKey("subject.id"), primary_key=True),
)

class Experiment(Base):
    __tablename__ = "experiment"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    type: Mapped[int] = mapped_column()
    finished: Mapped[bool] = mapped_column(Boolean, default=False)
   
    data_points: Mapped[list["DataPoint"]] = relationship(
            back_populates="experiment",
            cascade="all, delete-orphan",
        )

    subjects: Mapped[list["Subject"]] = relationship(
        secondary=experiment_subject,
        back_populates="experiments",
    )


class DataPoint(Base):
    __tablename__ = "data_point"

    id: Mapped[int] = mapped_column(primary_key=True)
    real_value: Mapped[float] = mapped_column(Float)
    target_value: Mapped[float] = mapped_column(Float)
    
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiment.id"))
    experiment: Mapped["Experiment"] = relationship(back_populates="data_points")

class Subject(Base):
    __tablename__ = "subject"

    id: Mapped[int] = mapped_column(primary_key=True)
    gdpr_accepted: Mapped[bool] = mapped_column(Boolean, default=False)

    experiments: Mapped[list["Experiment"]] = relationship(
        secondary=experiment_subject,
        back_populates="subjects",
    )


def main() -> None:
    with Session(engine) as session:

        print("── 1. Eksperymenty - 2 wiersze ──")
        experiments = [
            Experiment(
                title=f"Tekst {i}",
                type=random.randint(1, 5),
            )
            for i in range(1, 3)
        ]
        session.add_all(experiments)
        session.flush()

        for exp in experiments:
            print(f"  + Experiment(id={exp.id}, title={exp.title!r}, "
                  f"type={exp.type}, created_at={exp.created_at}, "
                  f"finished={exp.finished})")

        print("\n── 2. Data_points - 20 wierszy (10 dla eksperymentu 1, 10 dla eksperymentu 2) ──")
        for exp in experiments:
            for _ in range(10):
                exp.data_points.append(
                    DataPoint(
                        real_value=random.random(),
                        target_value=random.random(),
                    )
                )
        
        session.flush()

        all_data_points = session.scalars(select(DataPoint)).all()
        for dp in all_data_points:
            print(f"  + DataPoint(id={dp.id}, "
                  f"real={dp.real_value:.4f}, target={dp.target_value:.4f}) "
                  f"-> Experiment ID: {dp.experiment_id}")

        print("\n── 3. Wyswietlenie tabel  ──")
        all_experiments = session.scalars(select(Experiment)).all()
        all_data_points = session.scalars(select(DataPoint)).all()

        print(f"  Experiments ({len(all_experiments)}):")
        for exp in all_experiments:
            print(f"    {exp.id:>2} | {exp.title:<20} | "
                  f"type={exp.type} | finished={exp.finished} | "
                  f"created_at={exp.created_at}")

        print(f"  DataPoints ({len(all_data_points)}):")
        for dp in all_data_points:
            print(f"    {dp.id:>2} | real={dp.real_value:.4f} | "
                  f"target={dp.target_value:.4f}")

        print("\n── 3.5. Agregacje DataPoints dla każdego eksperymentu ──")
        
        stmt = (
            select(
                Experiment.id,
                Experiment.title,
                func.count(DataPoint.id).label("points_count"),
                func.sum(DataPoint.real_value).label("sum_real"),
                func.avg(DataPoint.real_value).label("avg_real"),
                func.sum(DataPoint.target_value).label("sum_target"),
                func.avg(DataPoint.target_value).label("avg_target"),
            )
            .join(DataPoint, Experiment.id == DataPoint.experiment_id)
            .group_by(Experiment.id)
        )
        
        agregacje = session.execute(stmt).all()

        for row in agregacje:
            print(f"  Eksperyment ID={row[0]} ({row[1]!r}), liczba punktów: {row[2]}")
            print(f"    real_value   -> suma: {row[3]:.4f}, średnia: {row[4]:.4f}")
            print(f"    target_value -> suma: {row[5]:.4f}, średnia: {row[6]:.4f}")

        print("\n── 4. Aktualizacja: finished = True dla wszystkich eksperymentów ──")
        result = session.execute(
            update(Experiment)
            .where(Experiment.finished.is_(False))
            .values(finished=True)
        )
        print(f"  Zaktualizowano {result.rowcount} wierszy.")

        for exp in session.scalars(select(Experiment)).all():
            print(f"    {exp.id:>2} | {exp.title:<20} | finished={exp.finished}")

        print("\n── 5. Usuwanie wierszy ──")
        
        for exp in session.scalars(select(Experiment)).all():
            session.delete(exp)
            
        session.flush()  

        print(f"  Usunięto wszystkie dane.")

        session.commit()

    with Session(engine) as session:
        print("\n── Weryfikacja po commicie ──")
        count_exp = session.scalar(select(func.count()).select_from(Experiment))
        count_dp = session.scalar(select(func.count()).select_from(DataPoint))

        print(f"  Experiments w bazie: {count_exp}")
        print(f"  DataPoints w bazie:  {count_dp}")


if __name__ == "__main__":

    Base.metadata.create_all(engine)
    
    main()

print("zakonczenie programu")