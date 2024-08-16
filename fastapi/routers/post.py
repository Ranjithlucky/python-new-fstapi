from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

from sqlalchemy.orm import Session
from typing import Optional,List
import models,schemas,utils
from . import oauth
from database import get_db

router=APIRouter(
     tags=['post']
)

# router=APIRouter(
#     prefix="/posts"
# )



@router.get("/post",response_model=list[schemas.post])
def read_post(db:Session=Depends(get_db),current_user:int=Depends(oauth.get_current_user)):
    postgre=db.query(models.post).filter(models.post.owner_id==current_user.id).all()
    return postgre

# @app.get("/sqlalchemy")
# def test_post(db:Session=Depends(get_db)):
#     sqlal=db.query(models.post).all()
#     return{"message":sqlal}

# @app.post("/createpost",status_code=status.HTTP_201_CREATED)
# def create_post(new_post:add):
#     cursor.execute("""INSERT INTO ADD(title,content,published) VALUES( %s, %s, %s) RETURNING * """,(add.title,add.content,add.published))
#     new_postgre=cursor.fetchone()
#     return{"new_post":new_postgre}

@router.post("/createpost", status_code=status.HTTP_201_CREATED,response_model=schemas.post)
def create_post(new_post: schemas.postcreate,db:Session=Depends(get_db),current_user:int=Depends(oauth.get_current_user)):
    # cursor.execute(
    #     """INSERT INTO ADD(title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #     (new_post.title, new_post.content, new_post.published)
    # )
    # created_post = cursor.fetchone()
    # conn.commit()
    # new_one=models.post(title=new_post.title,content=new_post.content,published=new_post.published)
    
    new_one=models.post(owner_id=current_user.id,**new_post.dict())
    db.add(new_one)
    db.commit()
    db.refresh(new_one)
    return  new_one

@router.get("/post/{id}",response_model=schemas.post)
def get_post(id:int,db:Session=Depends(get_db),current_user:int=Depends(oauth.get_current_user)):
    # # cursor.execute(""" SELECT * from add WHERE id=1""")
    # cursor.execute(""" SELECT * from add WHERE id=%s""",(str(id)))
    # test_post=cursor.fetchone()
    id1=db.query(models.post).filter(models.post.id==id).first()
    
    
    if not id1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id :{id} is not found")
    if id1.owner_id !=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="NOT AUTHORIZED")
        # response.status_code=status.HTTP_404_NOT_FOUND
        # return{"Message":f"post with id :{id} is not found"}
        
    return id1

@router.delete("/post/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session=Depends(get_db),current_user:int=Depends(oauth.get_current_user)):
    # cursor.execute(""" DELETE  from add WHERE id=%s returning *""",(str(id)))
    # delete_post=cursor.fetchone()
    # conn.commit()
    
    delet_query=db.query(models.post).filter(models.post.id==id)
    delet=delet_query.first()
    
    
    if delet==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id :{id} is not found")
        
    if delet.owner_id !=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="NOT AUTHORIZED")
        
    delet_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/post/{id}",response_model=schemas.post)
def update_post(id: int, updated_post: schemas.postcreate,db:Session=Depends(get_db),current_user:int=Depends(oauth.get_current_user)):
    
    new_update=db.query(models.post).filter(models.post.id==id)
    
    column=new_update.first()
    

    if  column == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    if column.owner_id !=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="NOT AUTHORIZED")
        
    new_update.update(updated_post.dict(),synchronize_session=False)
    db.commit()

    return new_update.first()