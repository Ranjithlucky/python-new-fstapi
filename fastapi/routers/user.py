from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

from sqlalchemy.orm import Session
import models,schemas,utils
from database import get_db

router=APIRouter(
    tags=['users']
)
# router=APIRouter(
#     prefix="/posts"
# )


@router.post("/createuser", status_code=status.HTTP_201_CREATED,response_model=schemas.createmodel)
def create_user(user:schemas.UserCreate,db:Session=Depends(get_db)):
    #hash the password-user 
    # hashed_password = pwd_context.hash(str(password))password_str = str(password)
    
    hash=utils.hash(user.password)
    user.password=hash
    
    new_user=models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/users/{id}',response_model=schemas.createmodel)
def get_user(id:int,db:Session=Depends(get_db)):
    users2=db.query(models.User).filter(models.User.id==id).first()
    
    if not users2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id:{id} does not exists")
        
    return users2