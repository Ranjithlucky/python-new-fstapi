from fastapi import APIRouter,Depends,status,HTTPException,Response
from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordRequestForm
import models,schemas,utils
from database import get_db
from . import oauth



router=APIRouter(
    tags=['authorization']
    
)

# @router.get("/login")
# def login(user_crendital:schemas.authuser,db:Session=Depends(get_db)):
#     user=db.query(models.User).filter(models.User.email==user_crendital.email).first()
    
    
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Invalid Credentials")
#     if not utils.verify(user_crendital.password,user.password):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Invalid Credentials")
#     return{"token":"okay bro"}
        
@router.get("/login",response_model=schemas.Token)
def login(user_crendital: OAuth2PasswordRequestForm=Depends(), db: Session = Depends(get_db)):
    
    # #username and password
    # {
    #     "username":"abcd",
    #     "password":"cdef"
    # }
    user = db.query(models.User).filter(models.User.email == user_crendital.username).first()
    
    # Check if user exists
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials")
    
    
    # Verify the password
    if not utils.verify(user_crendital.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials")
    
    #create token ans return token
    access_token=oauth.create_token(data={"user_id":user.id})
    
    return {"access_token":access_token,"token_type":"bearer"}

