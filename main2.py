# ============================================================
# ============================================================

#Zadanie 2


# ============================================================
# ============================================================






from datetime import datetime
from sqlalchemy import create_engine, String, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column



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
