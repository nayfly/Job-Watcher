from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.source.SourceRead])
def list_sources(db: Session = Depends(deps.get_db)):
    return db.query(models.source.Source).all()


@router.post("/", response_model=schemas.source.SourceRead, status_code=status.HTTP_201_CREATED)
def create_source(
    source_in: schemas.source.SourceCreate, db: Session = Depends(deps.get_db)
):
    # check uniqueness
    url_str = str(source_in.url)
    existing = db.query(models.source.Source).filter(models.source.Source.url == url_str).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source with this URL already exists",
        )
    data = source_in.model_dump()
    data["url"] = str(data.get("url"))
    obj = models.source.Source(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
