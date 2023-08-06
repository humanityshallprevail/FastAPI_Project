import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine
from sqlalchemy.orm import  sessionmaker, Session
from app.model.base import Base
import os



class Menu(Base):
    __tablename__ = "menus"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    description = Column(String)

class SubMenu(Base):
    __tablename__ = "submenus"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    menu_id = Column(String, ForeignKey("menus.id", ondelete = "CASCADE"))
    description = Column(String)

class Dish(Base):
    __tablename__ = "dishes"

    id = Column(String, primary_key = True, index = True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    price = Column(String)
    submenu_id = Column(String, ForeignKey("submenus.id", ondelete ="CASCADE"))
    description = Column(String)


# DATABASE_URL = os.getenv('DATABASE_URL')
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)
