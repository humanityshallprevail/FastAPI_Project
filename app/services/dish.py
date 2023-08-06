from app.repository.dish import DishRepository
from app.schemas import DishCreate
from sqlalchemy.orm import Session

class DishService:

    @staticmethod
    def create_dish(db: Session, menu_id: str, submenu_id: str, dish: DishCreate):
        return DishRepository.create_dish(db, menu_id, submenu_id, dish)

    @staticmethod
    def read_dishes(db: Session, menu_id: str, submenu_id: str, skip: int = 0, limit: int = 100):
        return DishRepository.read_dishes(db, menu_id, submenu_id, skip, limit)

    @staticmethod
    def read_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str):
        return DishRepository.read_dish(db, menu_id, submenu_id, dish_id)

    @staticmethod
    def update_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str, dish: DishCreate):
        return DishRepository.update_dish(db, menu_id, submenu_id, dish_id, dish)

    @staticmethod
    def delete_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str):
        return DishRepository.delete_dish(db, menu_id, submenu_id, dish_id)

    @staticmethod
    def delete_all_dishes(db: Session, menu_id: str, submenu_id: str):
        return DishRepository.delete_all_dishes(db, menu_id, submenu_id)
