from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class MenuBase(BaseModel):
    title: str
    description: str

class MenuCreate(MenuBase):
    pass

class Menu(MenuBase):
    id: str #int
    submenus_count: Optional[int] = 0
    dishes_count: Optional[int] = 0
    model_config = ConfigDict(from_attributes = True)

#-------------------------------------

class SubMenuBase(BaseModel):
    title: str
    description: str

class SubMenuCreate(SubMenuBase):
    pass

class SubMenu(SubMenuBase):
    id: str
    title: str
    dishes_count: Optional[int] = 0
    model_config = ConfigDict(from_attributes = True)


#------------------------------------

class DishBase(BaseModel):
    title: str
    description: str
    price: str



class DishCreate(DishBase):
    pass

class DishModel(DishBase):
    id: str
    title: str
    price: str = Field(..., alias="_price")

    @property
    def price(self):
        return str(round(float(self._price), 2))

    model_config = ConfigDict(from_attributes = True)

