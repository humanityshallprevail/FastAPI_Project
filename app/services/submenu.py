from app.repository.submenu import SubMenuRepository
from app.schema.schemas import SubMenuCreate
from sqlalchemy.orm import Session

class SubMenuService:

    @staticmethod
    def create_submenu(db: Session, menu_id: str, submenu: SubMenuCreate):
        return SubMenuRepository.create_submenu(db, menu_id, submenu)

    @staticmethod
    def read_submenus(db: Session, menu_id: str, skip: int = 0, limit: int = 100):
        return SubMenuRepository.read_submenus(db, menu_id, skip, limit)

    @staticmethod
    def read_submenu(db: Session, menu_id: str, submenu_id: str):
        return SubMenuRepository.read_submenu(db, menu_id, submenu_id)

    @staticmethod
    def update_submenu(db: Session, menu_id: str, submenu_id: str, submenu: SubMenuCreate):
        return SubMenuRepository.update_submenu(db, menu_id, submenu_id, submenu)

    @staticmethod
    def delete_submenu(db: Session, menu_id: str, submenu_id: str):
        return SubMenuRepository.delete_submenu(db, menu_id, submenu_id)

    @staticmethod
    def delete_all_submenus(db: Session, menu_id: str):
        return SubMenuRepository.delete_all_submenus(db, menu_id)
