from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import Dish, Menu, SubMenu
from app.schema.schemas import Menu as MenuModel
from app.schema.schemas import MenuCreate


class MenuRepository:

    @staticmethod
    async def read_all_menus(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[dict]:

        dishes_subquery = select(
            SubMenu.id.label('submenu_id'),
            func.json_agg(
                func.json_build_object('id', Dish.id, 'title', Dish.title, 'description',
                                       Dish.description, 'price', Dish.price)
            ).label('dishes')
        ).outerjoin(Dish, Dish.submenu_id == SubMenu.id)\
            .group_by(SubMenu.id).subquery()

        submenus_subquery = select(
            Menu.id.label('menu_id'),
            func.json_agg(
                func.json_build_object('id', SubMenu.id, 'title', SubMenu.title, 'description',
                                       SubMenu.description, 'dishes', dishes_subquery.c.dishes)
            ).label('submenus')
        ).outerjoin(SubMenu, SubMenu.menu_id == Menu.id)\
            .outerjoin(dishes_subquery, dishes_subquery.c.submenu_id == SubMenu.id)\
            .group_by(Menu.id).subquery()

        stmt = select(
            Menu,
            submenus_subquery.c.submenus
        ).outerjoin(submenus_subquery, submenus_subquery.c.menu_id == Menu.id)\
            .offset(skip).limit(limit)

        result = await db.execute(stmt)
        menus_result = result.all()

        menus = []
        for menu, submenus in menus_result:
            menu_dict = menu.__dict__
            menu_dict['submenus'] = submenus
            menus.append(menu_dict)

        return menus

    @staticmethod
    async def create_menu(db: AsyncSession, menu: MenuCreate) -> MenuModel:

        db_menu = Menu(title=menu.title, description=menu.description)
        db.add(db_menu)
        await db.commit()
        await db.refresh(db_menu)
        return db_menu

    @staticmethod
    async def read_menus(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[MenuModel]:

        submenus_subquery = select(SubMenu.menu_id, func.count(SubMenu.id).label('submenus_count'))\
            .group_by(SubMenu.menu_id).subquery()

        dishes_subquery = select(SubMenu.menu_id, func.count(Dish.id).label('dishes_count'))\
            .join(Dish, Dish.submenu_id == SubMenu.id).group_by(SubMenu.menu_id).subquery()

        stmt = select(Menu, submenus_subquery.c.submenus_count, dishes_subquery.c.dishes_count)\
            .outerjoin(submenus_subquery, submenus_subquery.c.menu_id == Menu.id)\
            .outerjoin(dishes_subquery, dishes_subquery.c.menu_id == Menu.id)\
            .offset(skip).limit(limit)

        result = await db.execute(stmt)
        menus_result = result.all()

        menus = []
        for menu, submenus_count, dishes_count in menus_result:
            menu.submenus_count = submenus_count if submenus_count else 0
            menu.dishes_count = dishes_count if dishes_count else 0
            menus.append(menu)

        return menus

    @staticmethod
    async def read_menu(db: AsyncSession, menu_id: str) -> MenuModel:
        submenus_subquery = (
            select(SubMenu.menu_id)
            .add_columns(func.count(SubMenu.id).label('submenus_count'))
            .group_by(SubMenu.menu_id)
            .subquery()
        )

        dishes_subquery = (
            select(SubMenu.menu_id)
            .add_columns(func.count(Dish.id).label('dishes_count'))
            .join(Dish, Dish.submenu_id == SubMenu.id)
            .group_by(SubMenu.menu_id)
            .subquery()
        )

        main_query = select(
            Menu,
            submenus_subquery.c.submenus_count,
            dishes_subquery.c.dishes_count
        ).outerjoin(
            submenus_subquery, submenus_subquery.c.menu_id == Menu.id
        ).outerjoin(
            dishes_subquery, dishes_subquery.c.menu_id == Menu.id
        ).filter(Menu.id == menu_id)

        result = await db.execute(main_query)
        result_row = result.first()

        if not result_row:
            raise HTTPException(status_code=404, detail='menu not found')

        menu, submenus_count, dishes_count = result_row
        menu.submenus_count = submenus_count or 0
        menu.dishes_count = dishes_count or 0

        return menu

    @staticmethod
    async def update_menu(db: AsyncSession, menu_id: str, menu: MenuCreate) -> MenuModel:
        result = await db.execute(select(Menu).filter(Menu.id == menu_id))
        db_menu = result.scalars().first()
        if not db_menu:
            raise HTTPException(status_code=404, detail='menu not found')
        for var, value in menu.model_dump().items():
            setattr(db_menu, var, value) if value else None
        await db.commit()
        await db.refresh(db_menu)
        return db_menu

    @staticmethod
    async def delete_menu(db: AsyncSession, menu_id: str) -> dict[str, str]:
        result = await db.execute(select(Menu).filter(Menu.id == menu_id))
        db_menu = result.scalars().first()
        if not db_menu:
            raise HTTPException(status_code=404, detail='menu not found')
        await db.delete(db_menu)
        await db.commit()
        return {'message': 'Menu deleted'}

    @staticmethod
    async def delete_all_menus(db: AsyncSession) -> dict[str, str]:
        await db.execute(delete(Dish))
        await db.execute(delete(SubMenu))
        await db.execute(delete(Menu))
        await db.commit()
        return {'message': 'All menus, submenus, and dishes have been deleted'}
