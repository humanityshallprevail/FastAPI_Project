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
        # Invalidate the cache for the menus list
        cache_key = 'menus-0-100'
        invalidate_cache(cache_key)

        return new_menu

    @staticmethod
    def read_menus(db: Session, skip: int = 0, limit: int = 100):
        cache_key = f'menus-{skip}-{limit}'

        # Try to get the result from the cache
        cached_menus = get_from_cache(cache_key)

        if cached_menus:
            logging.debug(f"Cache hit for key {cache_key}: {cached_menus.decode('utf-8')}")  # Debugging line
            return json.loads(cached_menus.decode('utf-8'))
        else:
            logging.debug(f'Cache miss for key {cache_key}')  # Debugging line

        # If not found in the cache, proceed to query the database
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
        # Serialize the result for caching

        json_menus = json.dumps(serialized_menus)
        # Cache the result
        set_in_cache(cache_key, json_menus)

        return menus

    @staticmethod
    def read_menu(db: Session, menu_id: str):
        menu = MenuRepository.read_menu(db, menu_id)
        return menu

    @staticmethod
    def update_menu(db: Session, menu_id: str, menu: MenuCreate):

        updated_menu = MenuRepository.update_menu(db, menu_id, menu)
        # Invalidate the cache for the menus list
        cache_key = 'menus-0-100'  # and any other keys that might be affected
        invalidate_cache(cache_key)

        return updated_menu

    @staticmethod
    def delete_menu(db: Session, menu_id: str):
        deleted_menu = MenuRepository.delete_menu(db, menu_id)

        # Invalidate the cache for the menus list
        cache_key = 'menus-0-100'  # and any other keys that might be affected
        invalidate_cache(cache_key)

        return deleted_menu

    @staticmethod
    def delete_all_menus(db: Session):
        deleted_menus = MenuRepository.delete_all_menus(db)

        # Invalidate all relevant cache keys
        # Here you might need to invalidate all keys that could be affected
        invalidate_cache('menus-0-100')
        # Add more keys if needed

        return deleted_menus
