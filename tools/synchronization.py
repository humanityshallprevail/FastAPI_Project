import logging

from sqlalchemy import select

from app.cache_manager import invalidate_cache
from app.model.models import Dish, Menu, SubMenu

logging.basicConfig(level=logging.DEBUG)


async def synchronize_menus(session, menus):

    invalidated_keys = []

    existing_menus_query = await session.execute(select(Menu))

    existing_menus = {menu.id: menu for menu in existing_menus_query.scalars().all()}

    remaining_submenus_to_delete = []
    remaining_dishes_to_delete = []
    for menu in menus:
        current_id = menu['id']
        existing_menu = existing_menus.get(current_id)

        if existing_menu:

            existing_menu.title = menu['title']
            existing_menu.description = menu['description']
            invalidated_keys.append(f'menus-{existing_menu.id}')

            submenus = menu['submenus']

            result_submenus = await session.execute(select(SubMenu).filter(SubMenu.menu_id == current_id))
            existing_submenus = {submenu.id: submenu for submenu in result_submenus.scalars().all()}

            for submenu in submenus:
                logging.info(f'We are running now submenus {submenu}')
                current_id_submenu = submenu['id']
                existing_submenu = existing_submenus.get(current_id_submenu)

                if existing_submenu:

                    existing_submenu.title = submenu['title']
                    existing_submenu.description = submenu['description']

#                   dish logic....
                    dishes = submenu['dishes']
                    result_dishes = await session.execute(select(Dish).filter(Dish.submenu_id == current_id_submenu))
                    existing_dishes = {dish.id: dish for dish in result_dishes.scalars().all()}

                    for dish in dishes:
                        current_dish_id = dish['id']
                        existing_dish = existing_dishes.get(current_dish_id)

                        if existing_dish:
                            existing_dish.title = dish['title']
                            existing_dish.description = dish['description']
                            if dish['discount'] is not None:
                                existing_dish.price = str(float(dish['price']) * (1 - dish['discount']))
                            else:
                                existing_dish.price = dish['price']
                            await invalidate_cache(f'dishes-{current_id}-{current_id_submenu}-{current_dish_id}')
                            del existing_dishes[dish['id']]
                        else:
                            if dish['discount'] is not None:
                                new_price = str(float(dish['price']) * (1 - dish['discount']))
                            else:
                                new_price = dish['price']
                            new_dish = Dish(id=dish['id'], title=dish['title'], submenu_id=current_id_submenu,
                                            price=new_price, description=dish['description'])
                            session.add(new_dish)
                            # Invalidate cache if needed
                            await invalidate_cache(f'dishes-{current_id}-{current_id_submenu}-{current_dish_id}')
                            await invalidate_cache(f'dishes-{current_id}-{current_id_submenu}-0-100')
                            await invalidate_cache(f'submenu-{current_id}-{current_id_submenu}')
                            await invalidate_cache(f'submenus-{current_id}-0-100')
                            await invalidate_cache(f'menus-{current_id}')
                            await invalidate_cache('menus-0-100')

                    remaining_dishes_to_delete.extend(existing_dishes.values())
#                   dish logic....
                    await invalidate_cache(f'submenu-{current_id}-{current_id_submenu}')
                    del existing_submenus[submenu['id']]

                else:

                    new_submenu = SubMenu(id=current_id_submenu,
                                          title=submenu['title'], menu_id=current_id, description=submenu['description'])
                    session.add(new_submenu)
                    await invalidate_cache(f'submenu-{current_id}-{current_id_submenu}')
                    await invalidate_cache(f'submenus-{current_id}-0-100')
                    await invalidate_cache(f'menus-{current_id}')
                    await invalidate_cache('menus-0-100')

            remaining_submenus_to_delete.extend(existing_submenus.values())

            del existing_menus[menu['id']]

        else:

            new_menu = Menu(id=menu['id'], title=menu['title'], description=menu['description'])
            session.add(new_menu)

    for remaining_menu_id in existing_menus.keys():
        result = await session.execute(select(Menu).filter(Menu.id == remaining_menu_id))

        db_menu = result.scalars().first()
        if db_menu:

            await session.delete(db_menu)
            invalidated_keys.append(f'menus-{remaining_menu_id}')

    for remaining_submenu in remaining_submenus_to_delete:
        menu_id = remaining_submenu.menu_id
        submenu_id = remaining_submenu.id

        result = await session.execute(select(SubMenu).filter(SubMenu.id == submenu_id))
        db_submenu = result.scalars().first()

        if db_submenu:
            await session.delete(db_submenu)

            cache_key_single = f'submenu-{menu_id}-{submenu_id}'
            await invalidate_cache(cache_key_single)

            cache_key_list = f'submenus-{menu_id}-0-100'
            await invalidate_cache(cache_key_list)

    for remaining_dish in remaining_dishes_to_delete:

        dish_id = remaining_dish.id
        submenu_id = remaining_dish.submenu_id

        result_submenu = await session.execute(select(SubMenu).filter(SubMenu.id == submenu_id))
        db_submenu = result_submenu.scalars().first()
        menu_id = db_submenu.menu_id if db_submenu else None

        result_dish = await session.execute(select(Dish).filter(Dish.id == dish_id))
        db_dish = result_dish.scalars().first()

        if db_dish:
            await session.delete(db_dish)

            cache_key_dish = f'dish-{menu_id}-{submenu_id}-{dish_id}'
            await invalidate_cache(cache_key_dish)

            cache_key_dishes = f'dishes-{menu_id}-{submenu_id}-0-100'
            await invalidate_cache(cache_key_dishes)

            cache_key_submenu = f'submenu-{menu_id}-{submenu_id}'
            await invalidate_cache(cache_key_submenu)

            cache_key_submenus = f'submenus-{menu_id}-0-100'
            await invalidate_cache(cache_key_submenus)

            cache_key_menu = f'menus-{menu_id}'
            await invalidate_cache(cache_key_menu)

            cache_key_menu_all = 'menus-0-100'
            await invalidate_cache(cache_key_menu_all)

    await session.commit()

    return invalidated_keys
