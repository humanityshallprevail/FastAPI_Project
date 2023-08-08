from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.model.models import Dish, SubMenu
from app.schema.schemas import DishCreate, DishModel


class DishRepository:

    @staticmethod
    def create_dish(db: Session, menu_id: str, submenu_id: str, dish: DishCreate) -> DishModel:
        db_dish = Dish(title=dish.title, description=dish.description, price=dish.price, submenu_id=submenu_id)
        db.add(db_dish)
        db.commit()
        db.refresh(db_dish)
        return db_dish

    @staticmethod
    def read_dishes(db: Session, menu_id: str, submenu_id: str, skip: int = 0, limit: int = 100) -> list[DishModel]:
        dishes = db.query(Dish).filter(Dish.submenu_id == submenu_id).offset(skip).limit(limit).all()
        return dishes

    @staticmethod
    def read_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str) -> DishModel:
        dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
        if dish is None:
            raise HTTPException(status_code=404, detail='dish not found')
        return dish

    @staticmethod
    def update_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str, dish: DishCreate) -> DishModel:
        db_dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
        if not db_dish:
            raise HTTPException(status_code=404, detail='dish not found')
        db_dish.title = dish.title
        db_dish.price = dish.price
        db_dish.description = dish.description
        db.commit()
        db.refresh(db_dish)
        return db_dish

    @staticmethod
    def delete_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str) -> dict[str, str]:
        db_dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
        if not db_dish:
            raise HTTPException(status_code=404, detail='dish not found')

        # Delete the dish
        db.delete(db_dish)
        db.commit()
        return {'message': 'Dish deleted'}

    @staticmethod
    def delete_all_dishes(db: Session, menu_id: str, submenu_id: str) -> dict[str, str]:

        db_submenu = db.query(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).first()
        if not db_submenu:
            raise HTTPException(status_code=404, detail='submenu not found')

        db.query(Dish).filter(Dish.submenu_id == submenu_id).delete(synchronize_session='fetch')
        db.commit()

        return {'message': 'All dishes for the given submenu have been deleted'}
