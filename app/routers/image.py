from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from .. import schemas, models, utils, oauth2
from ..database import get_db
import os
from datetime import datetime
from typing import List
from starlette.responses import FileResponse

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

    if not os.path.exists(image_path):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save image")

    new_image = models.Image(name=image.filename, path=image_path, size=os.path.getsize(image_path), type=image.content_type, dimensions="100x100", owner_id=current_user.id)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return new_image

@router.get("", response_model=List[schemas.Image])
async def get_images(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Dohvati sve slike za trenutnog korisnika iz baze
    images = db.query(models.Image).filter(models.Image.owner_id == current_user.id).all()

    # Pretvori objekte slika u oblike podataka za vraćanje
    image_data = []
    for image in images:
        image_data.append({
            "id": image.id,
            "name": image.name,
            "size": image.size,
            "type": image.type,
            "dimensions": image.dimensions,
            "owner_id": image.owner_id,
            "path": image.path  # Dodaj path kao polje u podacima slike
        })

    return image_data

@router.get('/{full_path:path}')
async def get_image(full_path: str):
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(full_path, media_type="image/png")


@router.delete('/{image_id:path}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    print(image_id)
    normalized_path = image_id.replace("/", "\\")
    print(normalized_path)
    image = db.query(models.Image).filter(models.Image.path == normalized_path, models.Image.owner_id == current_user.id).first()
    print(image)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    if os.path.exists(image_id):
        os.remove(image_id)

    db.delete(image)
    db.commit()
    print("Deleted")
    return Response(status_code=status.HTTP_204_NO_CONTENT)