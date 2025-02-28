from typing import Annotated

from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException, status
from models import Users
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .auth import bcrypt_context, get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_depenency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserPhoneVerification(BaseModel):
    password: str
    new_phone_number: str = Field(..., min_length=10, max_length=15)


@router.get("/get_user", status_code=status.HTTP_200_OK)
async def read_user_details(db: db_depenency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    payload = {
        "id": user_model.id,
        "username": user_model.username,
        "email": user_model.email,
        "first_name": user_model.first_name,
        "last_name": user_model.last_name,
        "role": user_model.role,
        "phone_number": user_model.phone_number,
    }

    return payload


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: db_depenency, user: user_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Password")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put("/change_phone_number", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(db: db_depenency, user: user_dependency, user_verification: UserPhoneVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Password")
    user_model.phone_number = user_verification.new_phone_number
    db.add(user_model)
    db.commit()
