from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from gestor.crud import instances
from gestor.models.instances import Base
from gestor.schemas.instances import Instance
from gestor.utils.database import SessionLocal, engine
from gestor.manager import manager

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


@router.get("/instances/", response_model=list[Instance])
def read_instances(db: Session = Depends(get_db)):
    db_instances = instances.get_instances(db)
    return db_instances


@router.get("/instances/{instance_id}", response_model=Instance)
def read_instance(instance_id: int, db: Session = Depends(get_db)):
    db_instance = instances.get_instance(db, instance_id=instance_id)
    if db_instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return db_instance
