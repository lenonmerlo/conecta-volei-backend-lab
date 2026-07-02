from datetime import date as Date
from datetime import time as Time

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GameModel(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    date: Mapped[Date] = mapped_column(nullable=False)
    location: Mapped[str] = mapped_column(String(160), nullable=False)
    time: Mapped[Time] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)