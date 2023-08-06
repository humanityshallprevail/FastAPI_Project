import uuid

from sqlalchemy import Column, ForeignKey, String

from app.model.base import Base


class Menu(Base):
    __tablename__ = 'menus'

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    description = Column(String)


class SubMenu(Base):
    __tablename__ = 'submenus'

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    menu_id = Column(String, ForeignKey('menus.id', ondelete='CASCADE'))
    description = Column(String)


class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    price = Column(String)
    submenu_id = Column(String, ForeignKey('submenus.id', ondelete='CASCADE'))
    description = Column(String)
