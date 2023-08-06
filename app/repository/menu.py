from app.models import Menu, SubMenu, Dish
from app.schemas import MenuCreate, Menu as MenuModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

class MenuRepository:

    @staticmethod
    def create_menu(db: Session, menu: MenuCreate):

        db_menu = Menu(title=menu.title, description=menu.description)
        db.add(db_menu)
        db.commit()
        db.refresh(db_menu)
        return db_menu

    @staticmethod
    def read_menus(db: Session, skip: int = 0, limit: int = 100):

        subquery = db.query(
            SubMenu.menu_id,
            func.count(SubMenu.id).label("submenus_count"),
            func.count(Dish.id).label("dishes_count")
        ).join(Dish, Dish.submenu_id == SubMenu.id).group_by(SubMenu.menu_id).subquery()

        menus = db.query(
            Menu,
            subquery.c.submenus_count,
            subquery.c.dishes_count
        ).outerjoin(
            subquery, subquery.c.menu_id == Menu.id
        ).offset(skip).limit(limit).all()


        for menu, submenus_count, dishes_count in menus:
            menu.submenus_count = submenus_count if submenus_count else 0
            menu.dishes_count = dishes_count if dishes_count else 0


        return [menu for menu, _, _ in menus]

    @staticmethod
    def read_menu(db: Session, menu_id: str):

        submenus_subquery = db.query(
            SubMenu.menu_id,
            func.count(SubMenu.id).label("submenus_count")
        ).group_by(SubMenu.menu_id).subquery()

        dishes_subquery = db.query(
            SubMenu.menu_id,
            func.count(Dish.id).label("dishes_count")
        ).join(Dish, Dish.submenu_id == SubMenu.id).group_by(SubMenu.menu_id).subquery()

        result = db.query(
            Menu,
            submenus_subquery.c.submenus_count,
            dishes_subquery.c.dishes_count
        ).outerjoin(
            submenus_subquery, submenus_subquery.c.menu_id == Menu.id
        ).outerjoin(
            dishes_subquery, dishes_subquery.c.menu_id == Menu.id
        ).filter(Menu.id == menu_id).first()

        if not result:
            raise HTTPException(status_code=404, detail="menu not found")

        menu, submenus_count, dishes_count = result
        menu.submenus_count = submenus_count or 0
        menu.dishes_count = dishes_count or 0

        return menu


    @staticmethod
    def update_menu( db: Session, menu_id: str, menu: MenuCreate):
        db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
        if not db_menu:
            raise HTTPException(status_code=404, detail="menu not found")
        for var, value in menu.model_dump().items():
            setattr(db_menu, var, value) if value else None
        db.commit()
        db.refresh(db_menu)
        return db_menu


    @staticmethod
    def delete_menu( db: Session, menu_id: str):
        db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
        if not db_menu:
            raise HTTPException(status_code=404, detail="menu not found")
        db.delete(db_menu)
        db.commit()
        return {"message": "Menu deleted"}

    @staticmethod
    def delete_all_menus(db: Session):
        db.query(Dish).delete()
        db.query(SubMenu).delete()
        db.query(Menu).delete()
        db.commit()
        return {"message": "All menus, submenus, and dishes have been deleted"}
