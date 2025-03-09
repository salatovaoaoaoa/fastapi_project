from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from src.models.sellers import Seller
from src.schemas import CreatingSeller, UpdatingSeller, ReturnedAllSellers, ReturnedSeller
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session
from sqlalchemy.orm import selectinload

sellers_router = APIRouter(tags=["seller"], prefix="/seller")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# Ручка для создания записи о продавце в БД. Возвращает созданного продавца.
@sellers_router.post(
    "/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED
)  # Прописываем модель ответа
async def create_seller(
    seller: CreatingSeller,
    session: DBSession,
):  # прописываем модель валидирующую входные данные
    # session = get_async_session() вместо этого мы используем иньекцию зависимостей DBSession

    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_seller = Seller(
        **{
            "first_name": seller.first_name,
            "last_name": seller.last_name,
            "e_mail": seller.e_mail,
            "password": seller.password,
        }
    )

    session.add(new_seller)
    await session.flush()

    await session.refresh(new_seller, attribute_names=['books'])

    return new_seller


# Ручка, возвращающая всех продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    # Хотим видеть формат
    # sellers: [{"id": 1, "first_name": "blabla", ...., "e_mail": "test@test.ru"},{...}]
    query = select(Seller).options(selectinload(Seller.books))
    result = await session.execute(query)
    sellers = result.scalars().all()
    return {"sellers": sellers}


# Ручка для получения продавца по ИД
@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    query = select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
    result = await session.execute(query)
    seller = result.scalar_one_or_none()
    if seller:
        return seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления продавца
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    if deleted_seller:
        await session.delete(deleted_seller)
        await session.flush()
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о продавце
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_seller_data: UpdatingSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_seller_data.first_name
        updated_seller.last_name = new_seller_data.last_name
        updated_seller.e_mail = new_seller_data.e_mail

        await session.flush()
        
        await session.refresh(updated_seller, attribute_names=['books'])

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
