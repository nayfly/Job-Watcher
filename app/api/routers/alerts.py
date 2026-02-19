from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.alert.AlertRead])
def list_alerts(db: Session = Depends(deps.get_db)):
    return db.query(models.alert.Alert).all()
