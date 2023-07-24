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

def get_db():
    with SessionLocal() as db:
        yield db

app = FastAPI()

## ----------------------------- MENU


from fastapi import HTTPException

@app.post("/api/v1/menus", response_model=MenuModel, status_code=201)
async def create_menu(menu: MenuCreate, db: Session = Depends(get_db)):
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
async def read_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    menus = db.query(Menu).offset(skip).limit(limit).all()
    for menu in menus:
        menu.submenus_count = db.query(SubMenu).filter(SubMenu.menu_id == menu.id).count()
        menu.dishes_count = db.query(Dish).join(SubMenu).filter(SubMenu.menu_id == menu.id).count()
    return menus

@app.get("/api/v1/menus/{menu_id}", response_model=MenuModel)
async def read_menu(menu_id: str, db: Session = Depends(get_db)):
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if menu is None:
        raise HTTPException(status_code=404, detail="menu not found")

    menu.submenus_count = db.query(SubMenu).filter(SubMenu.menu_id == menu.id).count()
    menu.dishes_count = db.query(Dish).join(SubMenu).filter(SubMenu.menu_id == menu.id).count()

    return menu

@app.patch("/api/v1/menus/{menu_id}", response_model=MenuModel)
async def update_menu(menu_id: str, menu: MenuCreate, db: Session = Depends(get_db)):
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    for var, value in menu.dict().items():
        setattr(db_menu, var, value) if value else None
    db.commit()
    db.refresh(db_menu)
    return db_menu

@app.delete("/api/v1/menus/{menu_id}")
async def delete_menu(menu_id: str, db: Session = Depends(get_db)):
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    db.delete(db_menu)
    db.commit()
    return {"message": "Menu deleted"}

@app.delete("/api/v1/menus")
async def delete_all_menus(db: Session = Depends(get_db)):
    db.query(Dish).delete()
    db.query(SubMenu).delete()
    db.query(Menu).delete()
    db.commit()
    return {"message": "All menus, submenus, and dishes have been deleted"}



## ------------------------------ SUBMENUS


@app.post("/api/v1/menus/{menu_id}/submenus", response_model=SubMenuModel, status_code = 201)

async def create_submenu(menu_id: str, submenu: SubMenuCreate, db: Session = Depends(get_db)):

    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if db_menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    db_submenu = SubMenu(title=submenu.title, menu_id=menu_id, description=submenu.description)
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


@app.get("/api/v1/menus/{menu_id}/submenus", response_model=List[SubMenuModel])
async def read_submenus(menu_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    submenus = db.query(SubMenu).filter(SubMenu.menu_id == menu_id).offset(skip).limit(limit).all()
    return submenus


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=SubMenuModel)
async def read_submenu(menu_id: str, submenu_id: str, db: Session = Depends(get_db)):

    # print(f"Attempting to retrieve submenu with id {submenu_id} under menu {menu_id}")
    submenu = db.query(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).first()
    if submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")

    submenu.dishes_count = db.query(Dish).filter(Dish.submenu_id == submenu.id).count()

    return submenu

@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=SubMenuModel, status_code = 200)
async def update_submenu(menu_id: str, submenu_id: str, submenu: SubMenuCreate, db: Session = Depends(get_db)):

    db_submenu = db.query(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).first()
    if not db_submenu:
        raise HTTPException(status_code=404, detail="submenu not found")
    db_submenu.title = submenu.title
    db_submenu.description = submenu.description
    db.commit()
    db.refresh(db_submenu)
    return db_submenu

@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}")
async def delete_submenu(menu_id: str, submenu_id: str, db: Session = Depends(get_db)):

    db_submenu = db.query(SubMenu).filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).first()
    if not db_submenu:
        raise HTTPException(status_code=404, detail="submenu not found")
    db.query(Dish).filter(Dish.submenu_id == submenu_id).delete(synchronize_session='fetch')
    db.delete(db_submenu)
    db.commit()
    return {"message": "submenu deleted"}

@app.delete("/api/v1/menus/{menu_id}/submenus")
async def delete_all_submenus(menu_id: str, db: Session = Depends(get_db)):
    db.query(Dish).filter(Dish.menu_id == menu_id).delete()
    db.query(SubMenu).filter(SubMenu.menu_id == menu_id).delete()
    db.commit()
    return {"message": "All submenus and dishes for the given menu have been deleted"}



## ----------------------------- DISHES


@app.post("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=DishModel, status_code = 201)
async def create_dish(menu_id: str, submenu_id: str, dish: DishCreate, db: Session = Depends(get_db)):
    db_dish = Dish(title=dish.title, description=dish.description, price=dish.price,  submenu_id=submenu_id)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=List[DishModel])
async def read_dishes(menu_id: str, submenu_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dishes = db.query(Dish).filter(Dish.submenu_id == submenu_id).offset(skip).limit(limit).all()
    return dishes

@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=DishModel)
async def read_dish(menu_id: str, submenu_id: str, dish_id: str, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
    if dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    return dish


@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=DishModel, status_code = 200)
async def update_dish(menu_id: str, submenu_id: str, dish_id: str, dish: DishCreate, db: Session = Depends(get_db)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="dish not found")
    db_dish.title = dish.title  # Use title instead of name
    db_dish.price = dish.price
    db_dish.description = dish.description  # Make sure to also update the description
    db.commit()
    db.refresh(db_dish)
    return db_dish

@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
async def delete_dish(menu_id: str, submenu_id: str, dish_id: str, db: Session = Depends(get_db)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id, Dish.submenu_id == submenu_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="dish not found")

    # Delete the dish
    db.delete(db_dish)
    db.commit()
    return {"message": "Dish deleted"}

@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes")
async def delete_all_dishes(menu_id: str, submenu_id: str, db: Session = Depends(get_db)):
    db.query(Dish).filter(Dish.submenu_id == submenu_id).delete()
    db.commit()
    return {"message": "All dishes for the given submenu have been deleted"}

## -----------------------------

