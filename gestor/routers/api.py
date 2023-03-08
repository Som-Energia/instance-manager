from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from gestor.manager import manager
from gestor.models.git import GitInfoModel
from gestor.models.instance import InstanceModel
from gestor.schemas.git import GitInfo, GitInfoFilter
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
    new_instance = InstanceModel.create_instance(db=db, instance=instance)
    return new_instance


@router.get("/instances/", response_model=list[Instance])
def read_instances(db: Session = Depends(get_db)):
    instances = InstanceModel.get_instances(db=db)
    return instances


@router.get("/instances/{instance_name}", response_model=Instance)
def read_instance(instance_name: str, db: Session = Depends(get_db)):
    instance = InstanceModel.get_instance(db=db, instance_name=instance_name)
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance
