from app.repository.menu import MenuRepository
from app.schemas import MenuCreate
from sqlalchemy.orm import Session

class MenuService:

    @staticmethod
    def create_menu(db: Session, menu: MenuCreate):
        return MenuRepository.create_menu(db, menu)

    @staticmethod
    def read_menus(db: Session, skip: int = 0, limit: int = 100):
        return MenuRepository.read_menus(db, skip, limit)

    @staticmethod
    def read_menu(db: Session, menu_id: str):
        return MenuRepository.read_menu(db, menu_id)

    @staticmethod
    def update_menu(db: Session, menu_id: str, menu: MenuCreate):
        return MenuRepository.update_menu(db, menu_id, menu)

    @staticmethod
    def delete_menu(db: Session, menu_id: str):
        return MenuRepository.delete_menu(db, menu_id)

    @staticmethod
    def delete_all_menus(db: Session, menu_id: str):
        return MenuRepository.delete_all_menus(db)
