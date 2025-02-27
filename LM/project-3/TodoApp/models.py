from database import Base
from sqlalchemy import Boolean, Column, Integer, String


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=False)
    description = Column(String, index=False)
    priority = Column(Integer, index=False)
    complete = Column(Boolean, default=False, index=True)
