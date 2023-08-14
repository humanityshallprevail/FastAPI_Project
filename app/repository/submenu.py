from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import Dish, Menu, SubMenu
from app.schema.schemas import SubMenu as SubMenuModel
from app.schema.schemas import SubMenuCreate


class SubMenuRepository:

    @staticmethod
    async def create_submenu(db: AsyncSession, menu_id: str, submenu: SubMenuCreate) -> SubMenuModel:
        result = await db.execute(select(Menu).filter(Menu.id == menu_id))
        db_menu = result.scalar_one_or_none()
        if db_menu is None:
            raise HTTPException(status_code=404, detail='Menu not found')
        db_submenu = SubMenu(title=submenu.title, menu_id=menu_id, description=submenu.description)
        db.add(db_submenu)
        await db.commit()
        await db.refresh(db_submenu)
        return db_submenu

    @staticmethod
    async def read_submenus(db: AsyncSession, menu_id: str, skip: int = 0, limit: int = 100) -> list[SubMenuModel]:
        dishes_subquery = select(
            Dish.submenu_id,
            func.count(Dish.id).label('dishes_count')
        ).group_by(Dish.submenu_id).subquery()

        stmt = select(
            SubMenu,
            dishes_subquery.c.dishes_count
        ).outerjoin(
            dishes_subquery, dishes_subquery.c.submenu_id == SubMenu.id
        ).filter(SubMenu.menu_id == menu_id).offset(skip).limit(limit)

        result = await db.execute(stmt)
        submenus_result = result.all()

        submenus = []
        for submenu, dishes_count in submenus_result:
            submenu.dishes_count = dishes_count if dishes_count else 0
            submenus.append(submenu)

        return submenus

    @staticmethod
    async def read_submenu(db: AsyncSession, menu_id: str, submenu_id: str) -> SubMenuModel:
        dishes_subquery = select(
            Dish.submenu_id,
            func.count(Dish.id).label('dishes_count')
        ).group_by(Dish.submenu_id).subquery()

        stmt = select(
            SubMenu,
            dishes_subquery.c.dishes_count
        ).outerjoin(
            dishes_subquery, dishes_subquery.c.submenu_id == SubMenu.id
        ).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id)

        result = await db.execute(stmt)
        result_row = result.first()

        if not result_row:
            raise HTTPException(status_code=404, detail='submenu not found')

        submenu, dishes_count = result_row
        submenu.dishes_count = dishes_count or 0

        return submenu

    @staticmethod
    async def update_submenu(db: AsyncSession, menu_id: str, submenu_id: str, submenu: SubMenuCreate) -> SubMenuModel:
        result = await db.execute(select(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id))
        db_submenu = result.scalar_one_or_none()
        if not db_submenu:
            raise HTTPException(status_code=404, detail='submenu not found')
        db_submenu.title = submenu.title
        db_submenu.description = submenu.description
        await db.commit()
        await db.refresh(db_submenu)
        return db_submenu

    @staticmethod
    async def delete_submenu(db: AsyncSession, menu_id: str, submenu_id: str) -> dict[str, str]:
        result = await db.execute(select(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id))
        db_submenu = result.scalar_one_or_none()
        if not db_submenu:
            raise HTTPException(status_code=404, detail='submenu not found')
        await db.execute(delete(Dish).filter(Dish.submenu_id == submenu_id))
        await db.delete(db_submenu)
        await db.commit()
        return {'message': 'submenu deleted'}

    @staticmethod
    async def delete_all_submenus(db: AsyncSession, menu_id: str) -> dict[str, str]:
        submenus_result = await db.execute(select(SubMenu.id).filter(SubMenu.menu_id == menu_id))
        submenu_ids = [submenu.id for submenu in submenus_result.scalars().all()]
        await db.execute(delete(Dish).filter(Dish.submenu_id.in_(submenu_ids)))
        await db.execute(delete(SubMenu).filter(SubMenu.menu_id == menu_id))
        await db.commit()
        return {'message': 'All submenus and dishes for the given menu have been deleted'}
