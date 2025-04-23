from typing import Union
from fastapi import FastAPI, Depends, HTTPException
from pydantic import  BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas

# Buat semua tabel di database
models.Base.metadata.create_all(bind=engine)
# Dependency untuk session database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}\

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/user/create",response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Cek apakah email sudah ada
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/user/all")
async def all_user(db: Session = Depends(get_db)):
    return db.query(models.User).all()