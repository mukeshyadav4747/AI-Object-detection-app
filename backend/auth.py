
import jwt, bcrypt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import models

SECRET_KEY = "ec65ff188dec27941b38995f1dd9f0aae9613c3dcc27e62622793c1c1b2f18df"
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=4)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def signup_user(db: Session, fullname: str, username: str, password: str):
    if db.query(models.User).filter_by(username=username).first():
        return False
    new_user = models.User(fullname=fullname, username=username, password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return True

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter_by(username=username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
