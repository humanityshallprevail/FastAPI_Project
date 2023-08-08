import json
import logging

from sqlalchemy.orm import Session

from app.cache_manager import get_from_cache, invalidate_cache, set_in_cache
from app.model.models import SubMenu as SubMenuModel
from app.repository.submenu import SubMenuRepository
from app.schema.schemas import SubMenuCreate


class SubMenuService:

    @staticmethod
    def create_submenu(db: Session, menu_id: str, submenu: SubMenuCreate) -> SubMenuModel:

        new_submenu = SubMenuRepository.create_submenu(db, menu_id, submenu)

        cache_key_list = f'submenus-{menu_id}-0-100'
        invalidate_cache(cache_key_list)

        cache_key_menu = f'menus-{menu_id}'
        invalidate_cache(cache_key_menu)

        cache_key_all = 'menus-0-100'
        invalidate_cache(cache_key_all)

        return new_submenu

    @staticmethod
    def read_submenus(db: Session, menu_id: str, skip: int = 0, limit: int = 100) -> list[SubMenuModel]:
        cache_key = f'submenus-{menu_id}-{skip}-{limit}'

        cached_submenus = get_from_cache(cache_key)

        if cached_submenus:
            logging.debug(f"Cache hit for key {cache_key}: {cached_submenus.decode('utf-8')}")
            return json.loads(cached_submenus.decode('utf-8'))
        else:
            logging.debug(f'Cache miss for key {cache_key}')

        submenus = SubMenuRepository.read_submenus(db, menu_id, skip, limit)

        serialized_submenus = [
            {
                'id': submenu.id,
                'title': submenu.title,
                'description': submenu.description,
                'dishes_count': submenu.dishes_count
            }
            for submenu in submenus
        ]

        json_submenus = json.dumps(serialized_submenus)
        logging.debug(f'Serialized submenu: {json_submenus}')
        set_in_cache(cache_key, json_submenus)

        return submenus

    @staticmethod
    def read_submenu(db: Session, menu_id: str, submenu_id: str) -> SubMenuModel:

        cache_key = f'submenu-{menu_id}-{submenu_id}'

        cached_submenu = get_from_cache(cache_key)

        if cached_submenu:
            logging.debug(f"Cache hit for key {cache_key}: {cached_submenu.decode('utf-8')}")
            return json.loads(cached_submenu.decode('utf-8'))
        else:
            logging.debug(f'Cache miss for key {cache_key}')

        submenu = SubMenuRepository.read_submenu(db, menu_id, submenu_id)

        serialized_submenu = {
            'id': submenu.id,
            'title': submenu.title,
            'description': submenu.description,
            'dishes_count': submenu.dishes_count
        }

        json_submenu = json.dumps(serialized_submenu)
        logging.debug(f'Serialized submenu: {json_submenu}')
        set_in_cache(cache_key, json_submenu)

        return submenu

    @staticmethod
    def update_submenu(db: Session, menu_id: str, submenu_id: str, submenu: SubMenuCreate) -> SubMenuModel:

        updated_submenu = SubMenuRepository.update_submenu(db, menu_id, submenu_id, submenu)

        cache_key_list = f'submenus-{menu_id}-0-100'
        invalidate_cache(cache_key_list)

        cache_key_menu = f'menus-{menu_id}'
        invalidate_cache(cache_key_menu)

        serialized_submenu = {
            'id': updated_submenu.id,
            'title': updated_submenu.title,
            'description': updated_submenu.description
        }
        cache_key_single = f'submenu-{menu_id}-{submenu_id}'
        json_submenu = json.dumps(serialized_submenu)
        set_in_cache(cache_key_single, json_submenu)

        return updated_submenu

    @staticmethod
    def delete_submenu(db: Session, menu_id: str, submenu_id: str) -> dict[str, str]:
        deleted_submenu = SubMenuRepository.delete_submenu(db, menu_id, submenu_id)

        cache_key_single = f'submenu-{menu_id}-{submenu_id}'
        invalidate_cache(cache_key_single)

        cache_key_list = f'submenus-{menu_id}-0-100'
        invalidate_cache(cache_key_list)

        cache_key_menu = f'menus-{menu_id}'
        invalidate_cache(cache_key_menu)

        cache_key_menu_all = 'menus-0-100'
        invalidate_cache(cache_key_menu_all)

        return deleted_submenu

    @staticmethod
    def delete_all_submenus(db: Session, menu_id: str) -> dict[str, str]:
        deleted_submenus = SubMenuRepository.delete_all_submenus(db, menu_id)

        cache_key_list = f'submenus-{menu_id}-0-100'
        invalidate_cache(cache_key_list)

        cache_key_menu_all = 'menus-0-100'
        invalidate_cache(cache_key_menu_all)

        return deleted_submenus
