from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import Dish, SubMenu
from app.schema.schemas import DishCreate, DishModel


class DishRepository:

    @staticmethod
    async def create_dish(db: AsyncSession, menu_id: str, submenu_id: str, dish: DishCreate) -> DishModel:
        db_dish = Dish(title=dish.title, description=dish.description, price=dish.price, submenu_id=submenu_id)
        db.add(db_dish)
        await db.commit()
        await db.refresh(db_dish)
        return db_dish

    @staticmethod
    async def read_dishes(db: AsyncSession, menu_id: str, submenu_id: str, skip: int = 0, limit: int = 100) -> list[DishModel]:
        result = await db.execute(select(Dish).filter(Dish.submenu_id == submenu_id).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def read_dish(db: AsyncSession, menu_id: str, submenu_id: str, dish_id: str) -> DishModel:
        result = await db.execute(select(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id))
        dish = result.scalar()
        if dish is None:
            raise HTTPException(status_code=404, detail='dish not found')
        return dish

    @staticmethod
    async def update_dish(db: AsyncSession, menu_id: str, submenu_id: str, dish_id: str, dish: DishCreate) -> DishModel:
        result = await db.execute(select(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id))
        db_dish = result.scalar()
        if not db_dish:
            raise HTTPException(status_code=404, detail='dish not found')
        db_dish.title = dish.title
        db_dish.price = dish.price
        db_dish.description = dish.description
        await db.commit()
        await db.refresh(db_dish)
        return db_dish

    @staticmethod
    async def delete_dish(db: AsyncSession, menu_id: str, submenu_id: str, dish_id: str) -> dict[str, str]:
        result = await db.execute(select(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id))
        db_dish = result.scalar()
        if not db_dish:
            raise HTTPException(status_code=404, detail='dish not found')
        await db.delete(db_dish)
        await db.commit()
        return {'message': 'Dish deleted'}

    @staticmethod
    async def delete_all_dishes(db: AsyncSession, menu_id: str, submenu_id: str) -> dict[str, str]:
        result = await db.execute(select(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id))
        db_submenu = result.scalar()
        if not db_submenu:
            raise HTTPException(status_code=404, detail='submenu not found')
        await db.execute(delete(Dish).filter(Dish.submenu_id == submenu_id))
        await db.commit()
        return {'message': 'All dishes for the given submenu have been deleted'}
