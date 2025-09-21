from sqlalchemy.orm import Session
from . import models

def create_uploaded_image(db: Session, filename: str, filepath: str):
    db_image = models.UploadedImage(filename=filename, filepath=filepath)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image
