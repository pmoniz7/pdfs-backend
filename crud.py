from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import models, schemas
from config import Settings
from botocore.exceptions import NoCredentialsError, BotoCoreError

print("%%%%%% 1- CRUD.PY %%%%%")

def create_pdf(db: Session, pdf: schemas.PDFRequest):
    db_pdf = models.PDF(name=pdf.name, selected=pdf.selected, file=pdf.file)
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf

print("%%%%%% 2- CRUD.PY %%%%%")

def read_pdfs(db: Session, selected: bool = None):
    if selected is None:
        return db.query(models.PDF).all()
    else:
        return db.query(models.PDF).filter(models.PDF.selected == selected).all()

print("%%%%%% 3- CRUD.PY %%%%%")

def read_pdf(db: Session, id: int):
    return db.query(models.PDF).filter(models.PDF.id == id).first()

print("%%%%%% 4- CRUD.PY %%%%%")

def update_pdf(db: Session, id: int, pdf: schemas.PDFRequest):
    db_pdf = db.query(models.PDF).filter(models.PDF.id == id).first()
    if db_pdf is None:
        return None
    update_data = pdf.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pdf, key, value)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf

print("%%%%%% 5- CRUD.PY %%%%%")

def delete_pdf(db: Session, id: int):
    db_pdf = db.query(models.PDF).filter(models.PDF.id == id).first()
    if db_pdf is None:
        return None
    db.delete(db_pdf)
    db.commit()
    return True

print("%%%%%% 6- CRUD.PY %%%%%")

def upload_pdf(db: Session, file: UploadFile, file_name: str):
    s3_client = Settings.get_s3_client()
    BUCKET_NAME = Settings().AWS_S3_BUCKET
    
    try:
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            file_name
        )
        file_url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}'

        print("%%%%% file_url %%%%%% ", file_url)
                        
        db_pdf = models.PDF(name=file.filename, selected=False, file=file_url)
        db.add(db_pdf)
        db.commit()
        db.refresh(db_pdf)
        return db_pdf
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Error in AWS credentials")


# def upload_pdf(db: Session, file: UploadFile, file_name: str):
#     s3_client = Settings.get_s3_client()
#     BUCKET_NAME = Settings().AWS_S3_BUCKET

#     try:
#         s3_client.upload_fileobj(
#             file.file,
#             BUCKET_NAME,
#             file_name,
#             ExtraArgs={'ACL': 'public-read'}
#         )
#         file_url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}'
        
#         db_pdf = models.PDF(name=file.filename, selected=False, file=file_url)
#         db.add(db_pdf)
#         db.commit()
#         db.refresh(db_pdf)
#         return db_pdf
#     except NoCredentialsError:
#         raise HTTPException(status_code=500, detail="Error in AWS credentials")
#     except BotoCoreError as e:
#         raise HTTPException(status_code=500, detail=str(e))