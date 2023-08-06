from app.models import Menu, SubMenu, Dish
from app.schemas import SubMenuCreate, SubMenu as SubMenuModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

class SubMenuRepository:

    @staticmethod
    def create_submenu(db: Session, menu_id: str, submenu: SubMenuCreate):
        db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
        if db_menu is None:
            raise HTTPException(status_code=404, detail="Menu not found")
        db_submenu = SubMenu(title=submenu.title, menu_id=menu_id, description=submenu.description)
        db.add(db_submenu)
        db.commit()
        db.refresh(db_submenu)
        return db_submenu


    @staticmethod
    def read_submenus(db: Session, menu_id: str, skip: int = 0, limit: int = 100):
        submenus = db.query(SubMenu).filter(SubMenu.menu_id == menu_id).offset(skip).limit(limit).all()
        return submenus

    @staticmethod
    def read_submenu(db: Session, menu_id: str, submenu_id: str):
        dishes_subquery = db.query(
            Dish.submenu_id,
            func.count(Dish.id).label("dishes_count")
        ).group_by(Dish.submenu_id).subquery()

        result = db.query(
            SubMenu,
            dishes_subquery.c.dishes_count
        ).outerjoin(
            dishes_subquery, dishes_subquery.c.submenu_id == SubMenu.id
        ).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="submenu not found")
        submenu, dishes_count = result
        submenu.dishes_count = dishes_count or 0

        return submenu

    @staticmethod
    def update_submenu(db: Session, menu_id: str, submenu_id: str, submenu: SubMenuCreate):
        db_submenu = db.query(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).first()
        if not db_submenu:
            raise HTTPException(status_code=404, detail="submenu not found")
        db_submenu.title = submenu.title
        db_submenu.description = submenu.description
        db.commit()
        db.refresh(db_submenu)
        return db_submenu

    @staticmethod
    def delete_submenu(db: Session, menu_id: str, submenu_id: str):
        db_submenu = db.query(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).first()
        if not db_submenu:
            raise HTTPException(status_code=404, detail="submenu not found")
        db.query(Dish).filter(Dish.submenu_id == submenu_id).delete(synchronize_session='fetch')
        db.delete(db_submenu)
        db.commit()
        return {"message": "submenu deleted"}

    @staticmethod
    def delete_all_submenus(db: Session, menu_id: str):
        db.query(Dish).filter(Dish.menu_id == menu_id).delete()
        db.query(SubMenu).filter(SubMenu.menu_id == menu_id).delete()
        db.commit()
        return {"message": "All submenus and dishes for the given menu have been deleted"}

