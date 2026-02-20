from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.watchlist.WatchlistRead])
def list_watchlists(db: Session = Depends(deps.get_db)):
    return db.query(models.watchlist.Watchlist).all()


@router.post(
    "/", response_model=schemas.watchlist.WatchlistRead, status_code=status.HTTP_201_CREATED
)
def create_watchlist(
    watchlist_in: schemas.watchlist.WatchlistCreate,
    db: Session = Depends(deps.get_db),
):
    data = watchlist_in.model_dump()
    obj = models.watchlist.Watchlist(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
