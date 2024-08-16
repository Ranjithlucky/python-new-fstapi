from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional

class add(BaseModel):
    title:str
    content:str
    published:bool=True

class postcreate(add):
    pass
class createmodel(BaseModel):
    id:int
    email:EmailStr
    created_time:datetime
    
    class config:
        orm_mode=True
class post(add):
    id:int
    # title:str
    # content:str
    # published:bool=True
    created_time:datetime
    owner_id:int
    owner:createmodel
    
    class config:
        orm_mode=True
        
class UserCreate(BaseModel):
    email:EmailStr
    password:str
    

        
class UserLogin(BaseModel):
    email:EmailStr
    password:str
    
class Token(BaseModel):
    access_token:str
    token_type:str
    
class TokenData(BaseModel):
    id: Optional[int] = None