from pydantic import BaseModel, ConfigDict


class MenuBase(BaseModel):
    title: str
    description: str


class MenuCreate(MenuBase):
    pass


class Menu(MenuBase):
    id: str  # int
    submenus_count: int | None = 0
    dishes_count: int | None = 0
    model_config = ConfigDict(from_attributes=True)

# -------------------------------------


class SubMenuBase(BaseModel):
    title: str
    description: str


class SubMenuCreate(SubMenuBase):
    pass


class SubMenu(SubMenuBase):
    id: str
    title: str
    dishes_count: int | None = 0
    model_config = ConfigDict(from_attributes=True)


# ------------------------------------

class DishBase(BaseModel):
    title: str
    description: str
    price: str


class DishCreate(DishBase):
    pass


class DishModel(DishBase):
    id: str

    @property
    def price(self):
        return str(round(float(self.price), 2))

    model_config = ConfigDict(from_attributes=True)
