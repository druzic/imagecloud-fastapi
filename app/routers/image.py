from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from .. import schemas, models, utils, oauth2
from ..database import get_db
import os
from datetime import datetime
from typing import List

router = APIRouter(
    prefix="/images",
    tags=["Images"]
)

UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.Image)
async def upload_image(image: UploadFile = File(...), db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    user_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename, file_extension = os.path.splitext(image.filename)
    unique_filename = f"{filename}_{timestamp}{file_extension}"

    if file_extension.lower() not in [".jpg", ".jpeg", ".png", ".gif"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type")

    image_path = os.path.join(user_dir, unique_filename)
    print(image_path)
    with open(image_path, "wb") as buffer:
        buffer.write(image.file.read())

    new_image = models.Image(name=image.filename, path=image_path, size=os.path.getsize(image_path), type=image.content_type, dimensions="100x100", owner_id=current_user.id)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return new_image

