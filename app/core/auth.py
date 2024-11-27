# app/core/auth.py
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database import get_db
from app.models.transaction import User
from app.schemas.user import Token, TokenData, UserCreate, User as UserSchema

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
  return pwd_context.hash(password)

def get_user(db: Session, email: str) -> User | None:
  return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> User | None:
  user = get_user(db, email)
  if not user or not verify_password(password, user.hashed_password):
      return None
  return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
  to_encode = data.copy()
  if expires_delta:
      expire = datetime.utcnow() + expires_delta
  else:
      expire = datetime.utcnow() + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(
      to_encode, 
      settings.SECRET_KEY, 
      algorithm=settings.ALGORITHM
  )
  return encoded_jwt

async def get_current_user(
  token: Annotated[str, Depends(oauth2_scheme)],
  db: Session = Depends(get_db)
) -> User:
  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
  )
  try:
      payload = jwt.decode(
          token, 
          settings.SECRET_KEY, 
          algorithms=[settings.ALGORITHM]
      )
      email: str = payload.get("sub")
      if email is None:
          raise credentials_exception
      token_data = TokenData(email=email)
  except JWTError:
      raise credentials_exception

  user = get_user(db, email=token_data.email)
  if user is None:
      raise credentials_exception
  return user

async def get_current_active_user(
  current_user: Annotated[User, Depends(get_current_user)]
) -> User:
  if not current_user.is_active:
      raise HTTPException(status_code=400, detail="Inactive user")
  return current_user

@router.post("/register", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
  db_user = get_user(db, email=user.email)
  if db_user:
      raise HTTPException(
          status_code=400,
          detail="Email already registered"
      )

  hashed_password = get_password_hash(user.password)
  db_user = User(
      email=user.email,
      hashed_password=hashed_password
  )

  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  db: Session = Depends(get_db)
):
  print(form_data.username)
  print(form_data.password
  )
  user = authenticate_user(db, form_data.username, form_data.password)
  if not user:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Incorrect username or password",
          headers={"WWW-Authenticate": "Bearer"},
      )

  access_token_expires = timedelta(
      minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
  )
  access_token = create_access_token(
      data={"sub": user.email},
      expires_delta=access_token_expires
  )
  return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserSchema)
async def read_users_me(
  current_user: Annotated[User, Depends(get_current_active_user)]
):
  return current_user