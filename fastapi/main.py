from fastapi import FastAPI,Response, status,HTTPException,Depends
from  fastapi.params import Body
from random import randrange
from sqlalchemy.orm import Session
import models,schemas,utils
from database import engine,get_db
from routers import post,user,auth,oauth

models.Base.metadata.create_all(bind=engine)

app=FastAPI()

my_post=[{"title":"the flower table","content":"show to go tomorrow","id":1},{"title":"enjoy every moment","content":"choose ur role to fight","id":4},{"title":"the flower table","content":"show to go tomorrow","id":3}]

def find_post(id):
    for post_id in my_post:
        if post_id['id']==id:
            return post_id
        


def find_index_post(id):
    for i,post_id in enumerate(my_post):
        if post_id['id']==id:
            return i


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root_api():
    return{"Hello":"world"}