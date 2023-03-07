from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import gestor.models.git as git_model
import gestor.models.instance as instance_model
from gestor.manager import manager
from gestor.schemas.git import GitInfo
from gestor.schemas.instance import Instance, InstanceCreate
from gestor.utils.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/instances/deploy/pr")
async def instance_from_pull_request(repository: str, pull_request: int) -> None:
    """Deploys a new instance from a pull request"""
    await manager.deploy_pull_request(repository, pull_request)


@router.post("/instances/", response_model=Instance)
def add_instance(instance: InstanceCreate, db: Session = Depends(get_db)):
    new_instance = instance_model.create_instance(db, instance)
    return new_instance


@router.get("/instances/", response_model=list[Instance])
def read_instances(db: Session = Depends(get_db)):
    instances = instance_model.get_instances(db)
    return instances


@router.get("/instances/{instance_id}", response_model=Instance)
def read_instance(instance_id: int, db: Session = Depends(get_db)):
    instance = instance_model.get_instance(db, instance_id=instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance
