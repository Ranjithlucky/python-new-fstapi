from sqlalchemy import Column,Integer,String,Boolean,ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from database import Base

class post(Base):
    __tablename__="add"
    
    id=Column(Integer,primary_key=True,nullable=True)
    title=Column(String,nullable=False)
    content=Column(String,nullable=False)
    published=Column(Boolean,server_default='True',nullable=False)
    created_time=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    owner_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    
    owner=relationship("User")
    
class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,nullable=True)
    email=Column(String,nullable=False,unique=True)
    password=Column(String,nullable=False)
    created_time=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    
# class auth(Base):
#     __tablename=""
    
    
    