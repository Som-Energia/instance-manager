from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from gestor.crud import instances
from gestor.models.instances import Base
from gestor.schemas.instances import Instance, InstanceCreate
from gestor.utils.database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/instances/", response_model=Instance)
def create_user(instance: InstanceCreate, db: Session = Depends(get_db)):
    db_instance = instances.search_instance(
        db,
        repository=instance.repository,
        pull_request=instance.pull_request,
    )
    if db_instance:
        raise HTTPException(status_code=400, detail="Instance already exists")
    return instances.create_instance(db=db, instance=instance)


@router.get("/instances/", response_model=list[Instance])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = instances.get_instances(db, skip=skip, limit=limit)
    return users


@router.get("/instances/{instance_id}", response_model=Instance)
def read_user(instance_id: int, db: Session = Depends(get_db)):
    db_instance = instances.get_instance(db, instance_id=instance_id)
    if db_instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return db_instance
