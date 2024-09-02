from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from pydantic.types import conint

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

class ImageUpload(BaseModel):
    path: str
    name: str
    size: str
    type: str
    dimensions: str

class Image(BaseModel):
    id: int
    name: str
    size: int
    type: str
    dimensions: str
    owner_id: int
    path: str

    class Config:
        from_attributes = True

class FolderCreate(BaseModel):
    name: str

class Folder(BaseModel):
    id: int
    name: str
    owner_id: int

    class Config:
        from_attributes = True

class FolderUpdate(BaseModel):
    image_path: str
    folder: str

class SharedFolder(BaseModel):
    folder: str
    email: str

class SharedFolderOut(BaseModel):
    id: int
    folder_id: int
    user_id: int
    shared_at: datetime

    class Config:
        from_attributes = True