import json
import logging

from sqlalchemy.orm import Session

from app.cache_manager import get_from_cache, invalidate_cache, set_in_cache
from app.repository.menu import MenuRepository
from app.schema.schemas import MenuCreate

logging.basicConfig(level=logging.DEBUG)


class MenuService:

    @staticmethod
    def create_menu(db: Session, menu: MenuCreate):
        new_menu = MenuRepository.create_menu(db, menu)
        cache_key = 'menus-0-100'
        invalidate_cache(cache_key)

        return new_menu

    @staticmethod
    def read_menus(db: Session, skip: int = 0, limit: int = 100):
        cache_key = f'menus-{skip}-{limit}'

        cached_menus = get_from_cache(cache_key)

        if cached_menus:
            logging.debug(f"Cache hit for key {cache_key}: {cached_menus.decode('utf-8')}")
            return json.loads(cached_menus.decode('utf-8'))
        else:
            logging.debug(f'Cache miss for key {cache_key}')

        menus = MenuRepository.read_menus(db, skip, limit)

        serialized_menus = [
            {
                'id': menu.id,
                'title': menu.title,
                'description': menu.description,
                'submenus_count': menu.submenus_count,
                'dishes_count': menu.dishes_count
            }
            for menu in menus
        ]

        json_menus = json.dumps(serialized_menus)
        set_in_cache(cache_key, json_menus)

        return menus

    @staticmethod
    def read_menu(db: Session, menu_id: str):
        cache_key = f'menus-{menu_id}'

        cached_menu = get_from_cache(cache_key)

        if cached_menu:
            logging.debug(f"Cache hit for key {cache_key}: {cached_menu.decode('utf-8')}")
            return json.loads(cached_menu.decode('utf-8'))
        else:
            logging.debug(f'Cache miss for key {cache_key}')

        menu = MenuRepository.read_menu(db, menu_id)

        serialized_menu = {
            'id': menu.id,
            'title': menu.title,
            'description': menu.description,
            'submenus_count': menu.submenus_count,
            'dishes_count': menu.dishes_count
        }

        json_menu = json.dumps(serialized_menu)

        set_in_cache(cache_key, json_menu)

        return menu

    @staticmethod
    def update_menu(db: Session, menu_id: str, menu: MenuCreate):

        updated_menu = MenuRepository.update_menu(db, menu_id, menu)

        serialized_menu = {
            'id': updated_menu.id,
            'title': updated_menu.title,
            'description': updated_menu.description
        }
        json_menu = json.dumps(serialized_menu)

        cache_key_menu = f'menus-{menu_id}'
        set_in_cache(cache_key_menu, json_menu)

        cache_key_list = 'menus-0-100'
        invalidate_cache(cache_key_list)

        return updated_menu

    @staticmethod
    def delete_menu(db: Session, menu_id: str):
        deleted_menu = MenuRepository.delete_menu(db, menu_id)

        cache_key = f'menus-{menu_id}'
        invalidate_cache(cache_key)

        cache_key = 'menus-0-100'
        invalidate_cache(cache_key)

        return deleted_menu

    @staticmethod
    def delete_all_menus(db: Session):
        deleted_menus = MenuRepository.delete_all_menus(db)

        invalidate_cache('menus-0-100')

        return deleted_menus
