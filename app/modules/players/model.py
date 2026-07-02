from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(80), nullable=True)
    whatsapp: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    gender: Mapped[str] = mapped_column(String(1), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    warnings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    skill_level: Mapped[float | None] = mapped_column(nullable=True)
    is_captain: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_setter: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    position: Mapped[str | None] = mapped_column(String(40), nullable=True)
