import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache_manager import get_from_cache, invalidate_cache, set_in_cache
from app.model.models import Menu as MenuModel
from app.repository.menu import MenuRepository
from app.schema.schemas import MenuCreate

logging.basicConfig(level=logging.DEBUG)


class MenuService:

    @staticmethod
    async def read_all_menus(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[dict]:
        menus = await MenuRepository.read_all_menus(db, skip, limit)
        return menus

    @staticmethod
    async def create_menu(db: AsyncSession, menu: MenuCreate) -> MenuModel:
        new_menu = await MenuRepository.create_menu(db, menu)
        cache_key = 'menus-0-100'
        await invalidate_cache(cache_key)

        return new_menu

    @staticmethod
    async def read_menus(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[MenuModel]:
        cache_key = f'menus-{skip}-{limit}'

        cached_menus = await get_from_cache(cache_key)

        if cached_menus:
            logging.debug(f"Cache hit for key {cache_key}: {cached_menus.decode('utf-8')}")
            return json.loads(cached_menus.decode('utf-8'))

        menus = await MenuRepository.read_menus(db, skip, limit)

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
        await set_in_cache(cache_key, json_menus)

        return menus

    @staticmethod
    async def read_menu(db: AsyncSession, menu_id: str) -> MenuModel:
        cache_key = f'menus-{menu_id}'

        cached_menu = await get_from_cache(cache_key)

        if cached_menu:
            logging.debug(f"Cache hit for key {cache_key}: {cached_menu.decode('utf-8')}")
            return json.loads(cached_menu.decode('utf-8'))
        else:
            logging.debug(f'Cache miss for key {cache_key}')

        menu = await MenuRepository.read_menu(db, menu_id)

        serialized_menu = {
            'id': menu.id,
            'title': menu.title,
            'description': menu.description,
            'submenus_count': menu.submenus_count,
            'dishes_count': menu.dishes_count
        }

        json_menu = json.dumps(serialized_menu)

        await set_in_cache(cache_key, json_menu)

        return menu

    @staticmethod
    async def update_menu(db: AsyncSession, menu_id: str, menu: MenuCreate) -> MenuModel:

        updated_menu = await MenuRepository.update_menu(db, menu_id, menu)

        serialized_menu = {
            'id': updated_menu.id,
            'title': updated_menu.title,
            'description': updated_menu.description
        }
        json_menu = json.dumps(serialized_menu)

        cache_key_menu = f'menus-{menu_id}'
        await set_in_cache(cache_key_menu, json_menu)

        cache_key_list = 'menus-0-100'
        await invalidate_cache(cache_key_list)

        return updated_menu

    @staticmethod
    async def delete_menu(db: AsyncSession, menu_id: str) -> dict[str, str]:
        deleted_menu = await MenuRepository.delete_menu(db, menu_id)

        cache_key = f'menus-{menu_id}'
        await invalidate_cache(cache_key)

        cache_key = 'menus-0-100'
        await invalidate_cache(cache_key)

        return deleted_menu

    @staticmethod
    async def delete_all_menus(db: AsyncSession) -> dict[str, str]:

        deleted_menus = await MenuRepository.delete_all_menus(db)

        await invalidate_cache('menus-0-100')

        return deleted_menus
