import logging

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.schema.schemas import DishCreate, DishModel
from app.schema.schemas import Menu as MenuModel
from app.schema.schemas import MenuCreate
from app.schema.schemas import SubMenu as SubMenuModel
from app.schema.schemas import SubMenuCreate
from app.services.dish import DishService as dish_service
from app.services.menu import MenuService as menu_service
from app.services.submenu import SubMenuService as submenu_service
from db.database import SessionLocal

logging.basicConfig(level=logging.DEBUG)


def get_db():
    with SessionLocal() as db:
        yield db


app = FastAPI()


# reverse function

@app.get('/items/{item_id}', name='get_item')
async def get_item(item_id: int):
    return {'item_id': item_id}

# ----------------------------- MENU


@app.post('/api/v1/menus', response_model=MenuModel, status_code=201)
def create_menu(menu: MenuCreate, db: Session = Depends(get_db)) -> MenuModel:
    """
    Create a new menu

    - **menu**: The menu details (JSON body)
    """

    return menu_service.create_menu(db, menu)


@app.get('/api/v1/menus', response_model=list[MenuModel])
def read_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[MenuModel]:
    """
    Retrieve a list of menus

    - **skip**: Number of records to skip (optional, default 0)
    - **limit**: Number of records to return (optional, default 100)
    """

    return menu_service.read_menus(db, skip, limit)


@app.get('/api/v1/menus/{menu_id}', response_model=MenuModel)
def read_menu(menu_id: str, db: Session = Depends(get_db)) -> MenuModel:
    """
    Retrieve a specific menu by ID

    - **menu_id**: The ID of the menu to retrieve
    """

    return menu_service.read_menu(db, menu_id)


@app.patch('/api/v1/menus/{menu_id}', response_model=MenuModel)
def update_menu(menu_id: str, menu: MenuCreate, db: Session = Depends(get_db)) -> MenuModel:
    """
    Update a specific menu by ID

    - **menu_id**: The ID of the menu to update
    - **menu**: The new menu details (JSON body)
    """

    return menu_service.update_menu(db, menu_id, menu)


@app.delete('/api/v1/menus/{menu_id}')
def delete_menu(menu_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Update a specific menu by ID

    - **menu_id**: The ID of the menu to update
    - **menu**: The new menu details (JSON body)
    """

    return menu_service.delete_menu(db, menu_id)


@app.delete('/api/v1/menus')
def delete_all_menus(db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Delete all menus
    """

    return menu_service.delete_all_menus(db)

# ------------------------------ SUBMENUS


@app.post('/api/v1/menus/{menu_id}/submenus', response_model=SubMenuModel, status_code=201)
def create_submenu(menu_id: str, submenu: SubMenuCreate, db: Session = Depends(get_db)) -> SubMenuModel:
    """
    Create a new submenu under a specific menu

    - **menu_id**: The ID of the parent menu
    - **submenu**: The submenu details (JSON body)
    """

    return submenu_service.create_submenu(db, menu_id, submenu)


@app.get('/api/v1/menus/{menu_id}/submenus', response_model=list[SubMenuModel])
def read_submenus(menu_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[SubMenuModel]:
    """
    Retrieve a list of submenus under a specific menu

    - **menu_id**: The ID of the parent menu
    - **skip**: Number of records to skip (optional, default 0)
    - **limit**: Number of records to return (optional, default 100)
    """

    return submenu_service.read_submenus(db, menu_id, skip, limit)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=SubMenuModel)
def read_submenu(menu_id: str, submenu_id: str, db: Session = Depends(get_db)) -> SubMenuModel:
    """
    Retrieve a specific submenu by ID

    - **menu_id**: The ID of the parent menu
    - **submenu_id**: The ID of the submenu to retrieve
    """

    return submenu_service.read_submenu(db, menu_id, submenu_id)


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=SubMenuModel, status_code=200)
def update_submenu(menu_id: str, submenu_id: str, submenu: SubMenuCreate, db: Session = Depends(get_db)) -> SubMenuModel:
    """
    Update a specific submenu by ID

    - **menu_id**: The ID of the parent menu
    - **submenu_id**: The ID of the submenu to update
    - **submenu**: The new submenu details (JSON body)
    """

    return submenu_service.update_submenu(db, menu_id, submenu_id, submenu)


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
def delete_submenu(menu_id: str, submenu_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Delete a specific submenu by ID

    - **menu_id**: The ID of the parent menu
    - **submenu_id**: The ID of the submenu to delete
    """

    return submenu_service.delete_submenu(db, menu_id, submenu_id)


@app.delete('/api/v1/menus/{menu_id}/submenus')
def delete_all_submenus(menu_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Delete all submenus under a specific menu

    - **menu_id**: The ID of the parent menu
    """

    return submenu_service.delete_all_submenus(db, menu_id)


# ----------------------------- DISHES


@app.post('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=DishModel, status_code=201)
def create_dish(menu_id: str, submenu_id: str, dish: DishCreate, db: Session = Depends(get_db)) -> DishModel:
    """
    Create a new dish under a specific submenu

    - **menu_id**: The ID of the parent menu
    - **submenu_id**: The ID of the parent submenu
    - **dish**: The dish details (JSON body)
    """

    return dish_service.create_dish(db, menu_id, submenu_id, dish)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=list[DishModel])
def read_dishes(menu_id: str, submenu_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[DishModel]:
    """
    Retrieve a list of dishes under a specific submenu

    - **menu_id**: The ID of the parent menu
    - **submenu_id**: The ID of the parent submenu
    - **skip**: Number of records to skip (optional, default 0)
    - **limit**: Number of records to return (optional, default 100)
    """

    return dish_service.read_dishes(db, menu_id, submenu_id, skip, limit)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishModel)
def read_dish(menu_id: str, submenu_id: str, dish_id: str, db: Session = Depends(get_db)) -> DishModel:
    """
    Retrieve a specific dish by ID

    - **menu_id**: The ID of the parent menu
    - **submenu_id**: The ID of the parent submenu
    - **dish_id**: The ID of the dish to retrieve
    """

    return dish_service.read_dish(db, menu_id, submenu_id, dish_id)


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishModel, status_code=200)
def update_dish(menu_id: str, submenu_id: str, dish_id: str, dish: DishCreate, db: Session = Depends(get_db)) -> DishModel:
    """
    Update a specific dish by ID

    - **menu_id**: The ID of the parent menu
    - **submenu_id**: The ID of the parent submenu
    - **dish_id**: The ID of the dish to update
    - **dish**: The new dish details (JSON body)
    """

    return dish_service.update_dish(db, menu_id, submenu_id, dish_id, dish)


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
def delete_dish(menu_id: str, submenu_id: str, dish_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Delete a specific dish by ID

    - **menu_id**: The ID of the parent menu
    - **submenu_id**: The ID of the parent submenu
    - **dish_id**: The ID of the dish to delete
    """

    return dish_service.delete_dish(db, menu_id, submenu_id, dish_id)


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes')
def delete_all_dishes(menu_id: str, submenu_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Delete all dishes under a specific submenu

    - **menu_id**: The ID of the parent menu
    - **submenu_id**: The ID of the parent submenu
    """

    return dish_service.delete_all_dishes(db, menu_id, submenu_id)
