from enum import Enum
from sqlalchemy import Boolean, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GroupEnum(str, Enum):
    CSC_1 = "東京CSC第一グループ"
    CSC_2 = "東京CSC第二グループ"
    CSC_N = "長岡CSCグループ"
    HHD = "HHDグループ"

class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True, index=True)
    ctstage_name: Mapped[str] = mapped_column(String, nullable=True)
    sweet_name: Mapped[str] = mapped_column(String, nullable=True)
    group: Mapped[GroupEnum] = mapped_column(SQLEnum(GroupEnum), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sv: Mapped[bool] = mapped_column(Boolean, default=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)