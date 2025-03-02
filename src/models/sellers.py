# У продавца есть обязательные поля:
# - id
# - first_name
# - last_name
# - e_mail
# - password

# должна быть ссылочка на модель book

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class Seller(BaseModel):
    __tablename__ = "sellers_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    e_mail: Mapped[str] = mapped_column(String(150), nullable=False)
    password: Mapped[str] = mapped_column(String(150), nullable=False)

    # связь One to Many
    books: Mapped[list["Book"]] = relationship(back_populates="seller")
