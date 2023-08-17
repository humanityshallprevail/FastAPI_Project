import asyncio
import logging
import time

from celery import Celery

from app.cache_manager import invalidate_cache
from app.main import get_db
from tools.parse_excel import parse_menu_excel
from tools.synchronization import synchronize_menus

logging.basicConfig(level=logging.DEBUG)


celery_app = Celery('myapp', broker='pyamqp://guest@rabbitmq//', backend='redis://redis:6379/0')
celery_app.config_from_object('app.celery_config')


has_run_once = False


@celery_app.task(bind=True)
def add_menu(self) -> None:

    global has_run_once

    if not has_run_once:
        time.sleep(30)
        has_run_once = True

    json_menu = parse_menu_excel('admin/Menu.xlsx')
    logging.info('Starting add_menu task.')

    async def async_add_menu():

        logging.info('async_add_menu')

        async for session in get_db():

            invalidated_keys = await synchronize_menus(session, json_menu)
            for key in invalidated_keys:
                await invalidate_cache(key)

            # Invalidate the list cache key as well
            await invalidate_cache('menus-0-100')

    loop = asyncio.get_event_loop()

    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(async_add_menu())
    logging.info('Task complete.')
