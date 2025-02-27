from typing import Annotated

import models
from database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, Path, status
from models import Todos
from pydantic import BaseModel, Field
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


@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(todo: TodoRequest, db: db_depenency, todo_id: Annotated[int, Path(..., gt=0)]):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    db.add(todo_model)
    db.commit()


@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: Annotated[int, Path(..., gt=0)], db: db_depenency):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo_model)
    db.commit()
