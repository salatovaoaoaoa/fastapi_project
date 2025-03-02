import pytest
from sqlalchemy import select
from src.models.sellers import Seller
from src.models.books import Book
from fastapi import status
from icecream import ic

# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "Tata",
        "last_name": "Popova",
        "e_mail": "test@example.com",
        "password": "securepassword",
    }
    response = await async_client.post("/api/v1/seller/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()
    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id, "Seller id not returned from endpoint"

    assert result_data == {
        "first_name": "Tata",
        "last_name": "Popova",
        "e_mail": "test@example.com",
    }

# Тест на получение всего списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller1 = Seller(first_name="Ivan", last_name="Ivanov", e_mail="ivanov@example.com", password="securepassword")
    seller2 = Seller(first_name="Petr", last_name="Petrov", e_mail="petrov@example.com", password="anotherpassword")
    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK
    sellers = response.json()['sellers']

    assert len(sellers) == 2  # два продавца
    assert all("password" not in seller for seller in sellers)  # Пароль не в ответе


# Тест на ручку получения продавца
@pytest.mark.asyncio
async def test_get_seller(db_session, async_client):
    seller = Seller(first_name="Sasha", last_name="Popov", e_mail="popov@test.com", password="superpuper12")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # данные продавца без пароля
    result_data = response.json()
    assert "password" not in result_data

# Тест на ручку обновления данных
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = Seller(first_name="Tanya", last_name="Salamatova", e_mail="salam@ttt.com", password="salamatovat1703")
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{seller.id}",
        json={"first_name": "Petr", "last_name": "Petrov", "e_mail": "petrov@example.com"},
    )

    assert response.status_code == status.HTTP_200_OK

    # данные продавца обновлены?
    updated_seller = await db_session.get(Seller, seller.id)
    assert updated_seller.first_name == "Petr"
    assert updated_seller.last_name == "Petrov"
    assert updated_seller.e_mail == "petrov@example.com"
    
    # Тест на удаление продавца и книг

@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = Seller(first_name="Ivan", last_name="Ivanov", e_mail="ivanov@example.com", password="securepassword")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # продавец и его книги удалены
    deleted_seller = await db_session.get(Seller, seller.id)
    assert deleted_seller is None

# Тест на продавца, которого нет в БД

@pytest.mark.asyncio
async def test_delete_nonexistent_seller(async_client):
    response = await async_client.delete(f"/api/v1/seller/9993039")

    assert response.status_code == status.HTTP_404_NOT_FOUND

# Тест на создание продавца без обязательных полей
@pytest.mark.asyncio
async def test_create_seller_invalid_data(async_client):
    data = {
        "last_name": "Popova",
        "e_mail": "test@example.com",
        "password": "securepassword",
    }
    response = await async_client.post("/api/v1/seller/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "first_name" in response.json()["detail"][0]["loc"]  # Должна быть ошибка для поля first_name
    
# Тест на запрос всех продавцов с пустой базой
@pytest.mark.asyncio
async def test_get_all_sellers_empty(db_session, async_client):
    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"sellers": []}
    
# Пытаюсь обновить продавца с некорректными данными

@pytest.mark.asyncio
async def test_update_seller_invalid_data(db_session, async_client):
    seller = Seller(first_name="Tanya", last_name="Salamatova", e_mail="salam@ttt.com", password="salamatovat1703")
    db_session.add(seller)
    await db_session.flush()

    # пропущу обязательное поле "first_name"
    response = await async_client.put(
        f"/api/v1/seller/{seller.id}",
        json={"last_name": "Petrov", "e_mail": "petrov@example.com"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "first_name" in response.json()["detail"][0]["loc"]
