from jose import JWTError,jwt
from datetime import datetime,timedelta
import schemas,models
from fastapi import FastAPI,Response, status,HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db

Oauth2_schema=OAuth2PasswordBearer(tokenUrl='login')
#secret_key
#algorithm
#expiration_time

SECRET_KEY="secret 6`12t78e278216767252w5"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTE=30

def create_token(data:dict):
    to_encode=data.copy()
    
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt
    
def verify_access_token(token:str,credentials_expression):
    try:
        
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        id:str=payload.get("user_id")
    
        if id is None:
           raise credentials_expression
        token_data=schemas.TokenData(id=id)
    except JWTError:
        raise credentials_expression
    
    return token_data
    
def get_current_user(token:str=Depends(Oauth2_schema),db:Session=Depends(get_db)):
    credentials_expression=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Could not validate credentails",headers={"WWW.AUTHENTICATE":"BEARER"})
    
    token=verify_access_token(token,credentials_expression)
    user3=db.query(models.User).filter(models.User.id==token.id).first()
    return user3