from app.models import Menu, SubMenu, Dish
from app.schemas import DishCreate, DishModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

class DishRepository:

    @staticmethod
    def create_dish(db: Session, menu_id: str, submenu_id: str, dish: DishCreate):
        db_dish = Dish(title=dish.title, description=dish.description, price=dish.price,  submenu_id=submenu_id)
        db.add(db_dish)
        db.commit()
        db.refresh(db_dish)
        return db_dish


    @staticmethod
    def read_dishes(db: Session, menu_id: str, submenu_id: str, skip: int = 0, limit: int = 100):
        dishes = db.query(Dish).filter(Dish.submenu_id == submenu_id).offset(skip).limit(limit).all()
        return dishes

    @staticmethod
    def read_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str):
        dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
        if dish is None:
            raise HTTPException(status_code=404, detail="dish not found")
        return dish


    @staticmethod
    def update_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str, dish: DishCreate):
        db_dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
        if not db_dish:
            raise HTTPException(status_code=404, detail="dish not found")
        db_dish.title = dish.title
        db_dish.price = dish.price
        db_dish.description = dish.description
        db.commit()
        db.refresh(db_dish)
        return db_dish

    @staticmethod
    def delete_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str):
        db_dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
        if not db_dish:
            raise HTTPException(status_code=404, detail="dish not found")

        # Delete the dish
        db.delete(db_dish)
        db.commit()
        return {"message": "Dish deleted"}

    @staticmethod
    def delete_all_dishes(db: Session, menu_id: str, submenu_id: str):
        db.query(Dish).filter(Dish.submenu_id == submenu_id).delete()
        db.commit()
        return {"message": "All dishes for the given submenu have been deleted"}


