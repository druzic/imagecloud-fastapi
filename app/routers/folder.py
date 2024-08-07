from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/folders",
    tags=["Folders"]
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.Folder)
def create_folder(folder: schemas.FolderCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    folder_data = folder.dict()
    folder_data['owner_id'] = current_user.id  # Set the owner_id here
    new_folder = models.Folder(**folder_data)
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return new_folder
