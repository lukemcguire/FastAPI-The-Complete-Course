from typing import Annotated

from pydantic import BaseModel, Field

import models
from database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, Path, status
from models import Todos
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_depenency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=3, max_length=100)
    priority: int = Field(..., ge=1, le=5)
    complete: bool

@app.get("/")
async def read_all(db: db_depenency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(todo_id: Annotated[int, Path(..., gt=0)], db: db_depenency):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoRequest, db: db_depenency):
    todo_model = Todos(**todo.model_dump())
    db.add(todo_model)
    db.commit()
