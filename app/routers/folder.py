from fastapi import APIRouter, Depends, status, HTTPException, Response
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

# @router.get("", response_model=list[schemas.Folder])
# def get_folders(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
#     folders = db.query(models.Folder).filter(models.Folder.owner_id == current_user.id).all()
#     return folders

@router.delete("/{folder_name:path}", status_code=status.HTTP_204_NO_CONTENT)
def get_folders(folder_name: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    folder = db.query(models.Folder).filter(models.Folder.name == folder_name, models.Folder.owner_id == current_user.id).first()
    db.delete(folder)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/{folder_name:path}')
async def get_images_from_folder(folder_name: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    folder = db.query(models.Folder).filter(models.Folder.name == folder_name, models.Folder.owner_id == current_user.id).first()
    if folder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")

    images = db.query(models.Image).filter(models.Image.owner_id == current_user.id, models.Image.folder == folder.id).all()

    return images

@router.post('/share', status_code=status.HTTP_201_CREATED, response_model=schemas.SharedFolderOut)
async def share_folder(folder_name: schemas.SharedFolder, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    print(folder_name)

    folder = db.query(models.Folder).filter(models.Folder.name == folder_name.folder, models.Folder.owner_id == current_user.id).first()
    if folder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    user = db.query(models.User).filter(models.User.email == folder_name.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    shared_folder = models.SharedFolders(folder_id=folder.id, user_id=user.id)
    db.add(shared_folder)
    db.commit()
    db.refresh(shared_folder)
    return shared_folder

@router.get('')
async def get_shared_folders(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    folders = db.query(models.Folder).filter(models.Folder.owner_id == current_user.id).all()
    share_folder = db.query(models.SharedFolders).filter(models.SharedFolders.user_id == current_user.id).all()
    for i in share_folder:
        print(i ,"bbb")
        folders.append(db.query(models.Folder).filter(models.Folder.id == i.folder_id).first())

    return folders