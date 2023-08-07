import json

from sqlalchemy.orm import Session

from app.cache_manager import get_from_cache, invalidate_cache, set_in_cache
from app.repository.dish import DishRepository
from app.schema.schemas import DishCreate


class DishService:

    @staticmethod
    def create_dish(db: Session, menu_id: str, submenu_id: str, dish: DishCreate):
        new_dish = DishRepository.create_dish(db, menu_id, submenu_id, dish)

        cache_key = f'dishes-{menu_id}-{submenu_id}-0-100'
        invalidate_cache(cache_key)

        return new_dish

    @staticmethod
    def read_dishes(db: Session, menu_id: str, submenu_id: str, skip: int = 0, limit: int = 100):
        cache_key = f'dishes-{menu_id}-{submenu_id}-{skip}-{limit}'

        cached_dishes = get_from_cache(cache_key)

        if cached_dishes:
            return json.loads(cached_dishes.decode('utf-8'))
        else:
            dishes = DishRepository.read_dishes(db, menu_id, submenu_id, skip, limit)
            serialized_dishes = [
                {
                    'id': dish.id,
                    'title': dish.title,
                    'description': dish.description,
                    'price': dish.price
                }
                for dish in dishes
            ]
            json_dishes = json.dumps(serialized_dishes)
            set_in_cache(cache_key, json_dishes)

            return dishes

    @staticmethod
    def read_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str):
        cache_key = f'dish-{menu_id}-{submenu_id}-{dish_id}'

        cached_dish = get_from_cache(cache_key)

        if cached_dish:
            return json.loads(cached_dish.decode('utf-8'))
        else:
            dish = DishRepository.read_dish(db, menu_id, submenu_id, dish_id)
            serialized_dish = {
                'id': dish.id,
                'title': dish.title,
                'description': dish.description,
                'price': dish.price
            }
            json_dish = json.dumps(serialized_dish)
            set_in_cache(cache_key, json_dish)

            return dish

    @staticmethod
    def update_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str, dish: DishCreate):
        updated_dish = DishRepository.update_dish(db, menu_id, submenu_id, dish_id, dish)

        cache_key = f'dish-{menu_id}-{submenu_id}-{dish_id}'
        invalidate_cache(cache_key)
        cache_key = f'dishes-{menu_id}-{submenu_id}-0-100'
        invalidate_cache(cache_key)

        return updated_dish

    @staticmethod
    def delete_dish(db: Session, menu_id: str, submenu_id: str, dish_id: str):
        deleted_dish = DishRepository.delete_dish(db, menu_id, submenu_id, dish_id)
        cache_key = f'dish-{menu_id}-{submenu_id}-{dish_id}'
        invalidate_cache(cache_key)
        cache_key = f'dishes-{menu_id}-{submenu_id}-0-100'
        invalidate_cache(cache_key)

        return deleted_dish

    @staticmethod
    def delete_all_dishes(db: Session, menu_id: str, submenu_id: str):
        deleted_dishes = DishRepository.delete_all_dishes(db, menu_id, submenu_id)

        cache_key = f'dishes-{menu_id}-{submenu_id}-0-100'
        invalidate_cache(cache_key)

        return deleted_dishes
