from pydantic import BaseModel, Field

from src.schemas.books import ReturnedBook

__all__ = ["CreatingSeller", "UpdatingSeller", "ReturnedSeller", "ReturnedAllSellers"]


# Базовый класс "Продавцы", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


# Класс для валидации создания объекта. Не содержит id так как его присваивает БД.
class CreatingSeller(BaseSeller):
    password: str = Field(..., min_length=8)


# Класс для обновления объекта, не содержит password и id (чтобы книги не поменялись)
class UpdatingSeller(BaseSeller):
    ...


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int
    books: list[ReturnedBook] = Field(default_factory=list)


# Класс для возврата массива объектов "Продавцы"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
