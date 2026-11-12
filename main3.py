# ============================================================
# ============================================================

#Zadanie 3

# ============================================================
# ============================================================






import random
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String, create_engine, delete, func, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass

class Base(DeclarativeBase):
    pass

# ---------- Tab Experiment ----------

class Experiment(Base):
    __tablename__ = "experiment"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    type: Mapped[int] = mapped_column()
    finished: Mapped[bool] = mapped_column(Boolean, default=False)


# ---------- Tab DataPoint ----------

class DataPoint(Base):
    __tablename__ = "data_point"

    id: Mapped[int] = mapped_column(primary_key=True)
    real_value: Mapped[float] = mapped_column(Float)
    target_value: Mapped[float] = mapped_column(Float)


# ---------- Połączenie z SQLite i utworzenie tab ----------

if __name__ == "__main__":
  
    engine = create_engine("sqlite:///experiments.db", echo=True)

 
    Base.metadata.create_all(engine)

print('Program został wykonany- utworzono tabele')


# =========================================================
# Dodanoe nowych danych 
# =========================================================

def main() -> None:
    # Utworzenie sesji
    with Session(engine) as session:

        # ─────────────────────────────────────────────
        #  Dodawanie wierszy do tabel 
        # ─────────────────────────────────────────────
        print("── 1. Eksperymemty - 2 wiersze ──")
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

        print("\n── 2. Data_points - 10 wierszt──")
        data_points = [
            DataPoint(
                real_value=random.random(),
                target_value=random.random(),
            )
            for _ in range(10)
        ]
        session.add_all(data_points)
        session.flush()

        for dp in data_points:
            print(f"  + DataPoint(id={dp.id}, "
                  f"real={dp.real_value:.4f}, target={dp.target_value:.4f})")

        # ─────────────────────────────────────────────
        # 2. Wyswietlenie danych 
        # ─────────────────────────────────────────────
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

        # ─────────────────────────────────────────────
        # 3. Aktualizacja: wszystkie Experiments → finished = True
        # ─────────────────────────────────────────────
        print("\n── 4. Aktualizacja: finished = True dla wszystkich eksperymentów ──")
        result = session.execute(
            update(Experiment)
            .where(Experiment.finished.is_(False))
            .values(finished=True)
        )
        print(f"  Zaktualizowano {result.rowcount} wierszy.")

        for exp in session.scalars(select(Experiment)).all():
            print(f"    {exp.id:>2} | {exp.title:<20} | finished={exp.finished}")

        # ─────────────────────────────────────────────
        # 4. Usunięcie  wierszy z obu tabel
        # ─────────────────────────────────────────────
        print("\n── 5. Usuwanie wierszy ──")
        deleted_dp = session.execute(delete(DataPoint)).rowcount
        deleted_exp = session.execute(delete(Experiment)).rowcount
        print(f"  Usunięto {deleted_dp} DataPoints i {deleted_exp} Experiments.")

        session.commit()

    # Osobna sesja do weryfikacji
    with Session(engine) as session:
        print("\n── Weryfikacja po commicie ──")
        count_exp = session.scalar(select(func.count()).select_from(Experiment))
        count_dp = session.scalar(select(func.count()).select_from(DataPoint))

        print(f"  Experiments w bazie: {count_exp}")
        print(f"  DataPoints w bazie:  {count_dp}")


if __name__ == "__main__":
    main()