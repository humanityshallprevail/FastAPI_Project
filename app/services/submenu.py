import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache_manager import get_from_cache, invalidate_cache, set_in_cache
from app.model.models import SubMenu as SubMenuModel
from app.repository.submenu import SubMenuRepository
from app.schema.schemas import SubMenuCreate


class SubMenuService:

    @staticmethod
    async def create_submenu(db: AsyncSession, menu_id: str, submenu: SubMenuCreate) -> SubMenuModel:

        new_submenu = await SubMenuRepository.create_submenu(db, menu_id, submenu)

        cache_key_list = f'submenus-{menu_id}-0-100'
        await invalidate_cache(cache_key_list)

        cache_key_menu = f'menus-{menu_id}'
        await invalidate_cache(cache_key_menu)

        cache_key_all = 'menus-0-100'
        await invalidate_cache(cache_key_all)

        return new_submenu

    @staticmethod
    async def read_submenus(db: AsyncSession, menu_id: str, skip: int = 0, limit: int = 100) -> list[SubMenuModel]:
        cache_key = f'submenus-{menu_id}-{skip}-{limit}'

        cached_submenus = await get_from_cache(cache_key)

        if cached_submenus:
            logging.debug(f"Cache hit for key {cache_key}: {cached_submenus.decode('utf-8')}")
            return json.loads(cached_submenus.decode('utf-8'))
        else:
            logging.debug(f'Cache miss for key {cache_key}')

        submenus = await SubMenuRepository.read_submenus(db, menu_id, skip, limit)

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
        await set_in_cache(cache_key, json_submenus)

        return submenus

    @staticmethod
    async def read_submenu(db: AsyncSession, menu_id: str, submenu_id: str) -> SubMenuModel:

        cache_key = f'submenu-{menu_id}-{submenu_id}'

        cached_submenu = await get_from_cache(cache_key)

        if cached_submenu:
            logging.debug(f"Cache hit for key {cache_key}: {cached_submenu.decode('utf-8')}")
            return json.loads(cached_submenu.decode('utf-8'))
        else:
            logging.debug(f'Cache miss for key {cache_key}')

        submenu = await SubMenuRepository.read_submenu(db, menu_id, submenu_id)

        serialized_submenu = {
            'id': submenu.id,
            'title': submenu.title,
            'description': submenu.description,
            'dishes_count': submenu.dishes_count
        }

        json_submenu = json.dumps(serialized_submenu)
        logging.debug(f'Serialized submenu: {json_submenu}')
        await set_in_cache(cache_key, json_submenu)

        return submenu

    @staticmethod
    async def update_submenu(db: AsyncSession, menu_id: str, submenu_id: str, submenu: SubMenuCreate) -> SubMenuModel:

        updated_submenu = await SubMenuRepository.update_submenu(db, menu_id, submenu_id, submenu)

        cache_key_list = f'submenus-{menu_id}-0-100'
        await invalidate_cache(cache_key_list)

        cache_key_menu = f'menus-{menu_id}'
        await invalidate_cache(cache_key_menu)

        serialized_submenu = {
            'id': updated_submenu.id,
            'title': updated_submenu.title,
            'description': updated_submenu.description
        }
        cache_key_single = f'submenu-{menu_id}-{submenu_id}'
        json_submenu = json.dumps(serialized_submenu)
        await set_in_cache(cache_key_single, json_submenu)

        return updated_submenu

    @staticmethod
    async def delete_submenu(db: AsyncSession, menu_id: str, submenu_id: str) -> dict[str, str]:
        deleted_submenu = await SubMenuRepository.delete_submenu(db, menu_id, submenu_id)

        cache_key_single = f'submenu-{menu_id}-{submenu_id}'
        await invalidate_cache(cache_key_single)

        cache_key_list = f'submenus-{menu_id}-0-100'
        await invalidate_cache(cache_key_list)

        cache_key_menu = f'menus-{menu_id}'
        await invalidate_cache(cache_key_menu)

        cache_key_menu_all = 'menus-0-100'
        await invalidate_cache(cache_key_menu_all)

        return deleted_submenu

    @staticmethod
    async def delete_all_submenus(db: AsyncSession, menu_id: str) -> dict[str, str]:
        deleted_submenus = await SubMenuRepository.delete_all_submenus(db, menu_id)

        cache_key_list = f'submenus-{menu_id}-0-100'
        await invalidate_cache(cache_key_list)

        cache_key_menu_all = 'menus-0-100'
        await invalidate_cache(cache_key_menu_all)

        return deleted_submenus
