from fastapi import FastAPI, Depends, HTTPException
from typing import List
import asyncio
from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from models import Menu, SessionLocal
from schemas import MenuCreate, Menu as MenuModel
from models import SubMenu
from schemas import SubMenuCreate, SubMenu as SubMenuModel
from models import Dish
from schemas import DishCreate, DishModel
from sqlalchemy import func



def get_db():
    with SessionLocal() as db:
        yield db

app = FastAPI()

## ----------------------------- MENU

@app.post("/api/v1/menus", response_model=MenuModel, status_code=201)
def create_menu(menu: MenuCreate, db: Session = Depends(get_db)):
    try:
        db_menu = Menu(title=menu.title, description=menu.description)
        db.add(db_menu)
        db.commit()
        db.refresh(db_menu)
        return db_menu
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="An error occurred.")


@app.get("/api/v1/menus", response_model=List[MenuModel])
def read_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    subquery = db.query(
        SubMenu.menu_id,
        func.count(SubMenu.id).label("submenus_count"),
        func.count(Dish.id).label("dishes_count")
    ).join(Dish, Dish.submenu_id == SubMenu.id).group_by(SubMenu.menu_id).subquery()

    menus = db.query(
        Menu,
        subquery.c.submenus_count,
        subquery.c.dishes_count
    ).outerjoin(
        subquery, subquery.c.menu_id == Menu.id
    ).offset(skip).limit(limit).all()


    for menu, submenus_count, dishes_count in menus:
        menu.submenus_count = submenus_count if submenus_count else 0
        menu.dishes_count = dishes_count if dishes_count else 0


    return [menu for menu, _, _ in menus]


@app.get("/api/v1/menus/{menu_id}", response_model=MenuModel)
def read_menu(menu_id: str, db: Session = Depends(get_db)):

    submenus_subquery = db.query(
        SubMenu.menu_id,
        func.count(SubMenu.id).label("submenus_count")
    ).group_by(SubMenu.menu_id).subquery()

    dishes_subquery = db.query(
        SubMenu.menu_id,
        func.count(Dish.id).label("dishes_count")
    ).join(Dish, Dish.submenu_id == SubMenu.id).group_by(SubMenu.menu_id).subquery()

    result = db.query(
        Menu,
        submenus_subquery.c.submenus_count,
        dishes_subquery.c.dishes_count
    ).outerjoin(
        submenus_subquery, submenus_subquery.c.menu_id == Menu.id
    ).outerjoin(
        dishes_subquery, dishes_subquery.c.menu_id == Menu.id
    ).filter(Menu.id == menu_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="menu not found")

    menu, submenus_count, dishes_count = result
    menu.submenus_count = submenus_count or 0
    menu.dishes_count = dishes_count or 0

    return menu


@app.patch("/api/v1/menus/{menu_id}", response_model=MenuModel)
def update_menu(menu_id: str, menu: MenuCreate, db: Session = Depends(get_db)):
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="menu not found")
    for var, value in menu.model_dump().items():
        setattr(db_menu, var, value) if value else None
    db.commit()
    db.refresh(db_menu)
    return db_menu


@app.delete("/api/v1/menus/{menu_id}")
def delete_menu(menu_id: str, db: Session = Depends(get_db)):
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="menu not found")
    db.delete(db_menu)
    db.commit()
    return {"message": "Menu deleted"}


@app.delete("/api/v1/menus")
def delete_all_menus(db: Session = Depends(get_db)):
    db.query(Dish).delete()
    db.query(SubMenu).delete()
    db.query(Menu).delete()
    db.commit()
    return {"message": "All menus, submenus, and dishes have been deleted"}


## ------------------------------ SUBMENUS


@app.post("/api/v1/menus/{menu_id}/submenus", response_model=SubMenuModel, status_code = 201)
def create_submenu(menu_id: str, submenu: SubMenuCreate, db: Session = Depends(get_db)):
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if db_menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    db_submenu = SubMenu(title=submenu.title, menu_id=menu_id, description=submenu.description)
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


@app.get("/api/v1/menus/{menu_id}/submenus", response_model=List[SubMenuModel])
def read_submenus(menu_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    submenus = db.query(SubMenu).filter(SubMenu.menu_id == menu_id).offset(skip).limit(limit).all()
    return submenus


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=SubMenuModel)
def read_submenu(menu_id: str, submenu_id: str, db: Session = Depends(get_db)):
    dishes_subquery = db.query(
        Dish.submenu_id,
        func.count(Dish.id).label("dishes_count")
    ).group_by(Dish.submenu_id).subquery()

    result = db.query(
        SubMenu,
        dishes_subquery.c.dishes_count
    ).outerjoin(
        dishes_subquery, dishes_subquery.c.submenu_id == SubMenu.id
    ).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="submenu not found")
    submenu, dishes_count = result
    submenu.dishes_count = dishes_count or 0

    return submenu


@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=SubMenuModel, status_code = 200)
def update_submenu(menu_id: str, submenu_id: str, submenu: SubMenuCreate, db: Session = Depends(get_db)):
    db_submenu = db.query(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).first()
    if not db_submenu:
        raise HTTPException(status_code=404, detail="submenu not found")
    db_submenu.title = submenu.title
    db_submenu.description = submenu.description
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}")
def delete_submenu(menu_id: str, submenu_id: str, db: Session = Depends(get_db)):
    db_submenu = db.query(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).first()
    if not db_submenu:
        raise HTTPException(status_code=404, detail="submenu not found")
    db.query(Dish).filter(Dish.submenu_id == submenu_id).delete(synchronize_session='fetch')
    db.delete(db_submenu)
    db.commit()
    return {"message": "submenu deleted"}

@app.delete("/api/v1/menus/{menu_id}/submenus")
def delete_all_submenus(menu_id: str, db: Session = Depends(get_db)):
    db.query(Dish).filter(Dish.menu_id == menu_id).delete()
    db.query(SubMenu).filter(SubMenu.menu_id == menu_id).delete()
    db.commit()
    return {"message": "All submenus and dishes for the given menu have been deleted"}


## ----------------------------- DISHES


@app.post("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=DishModel, status_code = 201)
def create_dish(menu_id: str, submenu_id: str, dish: DishCreate, db: Session = Depends(get_db)):
    db_dish = Dish(title=dish.title, description=dish.description, price=dish.price,  submenu_id=submenu_id)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=List[DishModel])
def read_dishes(menu_id: str, submenu_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dishes = db.query(Dish).filter(Dish.submenu_id == submenu_id).offset(skip).limit(limit).all()
    return dishes

@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=DishModel)
def read_dish(menu_id: str, submenu_id: str, dish_id: str, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
    if dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    return dish


@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=DishModel, status_code = 200)
def update_dish(menu_id: str, submenu_id: str, dish_id: str, dish: DishCreate, db: Session = Depends(get_db)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="dish not found")
    db_dish.title = dish.title
    db_dish.price = dish.price
    db_dish.description = dish.description
    db.commit()
    db.refresh(db_dish)
    return db_dish

@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
def delete_dish(menu_id: str, submenu_id: str, dish_id: str, db: Session = Depends(get_db)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="dish not found")

    # Delete the dish
    db.delete(db_dish)
    db.commit()
    return {"message": "Dish deleted"}

@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes")
def delete_all_dishes(menu_id: str, submenu_id: str, db: Session = Depends(get_db)):
    db.query(Dish).filter(Dish.submenu_id == submenu_id).delete()
    db.commit()
    return {"message": "All dishes for the given submenu have been deleted"}

## -----------------------------

