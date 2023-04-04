from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from gestor.manager import manager
from gestor.models.instance import InstanceModel
from gestor.schemas.instance import Instance
from gestor.utils.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
async def root():
    return {"message": "Hello API!"}


@router.post("/instances/deploy/pr")
async def instance_from_pull_request(
    repository: str, pull_request: int
) -> dict[str, str]:
    """Deploys a new instance from a pull request"""
    try:
        await manager.start_instance_from_pull_request(repository, pull_request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Added new instance from pull request task"}


@router.delete("/instances/{instance_name}")
async def undeploy_instance(instance_name: str, db: Session = Depends(get_db)) -> None:
    instance = InstanceModel.get_instance(db=db, instance_name=instance_name)
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    else:
        await Instance.from_orm(instance).undeploy()


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


@router.get("/instances/{instance_name}/logs", response_model=str)
async def read_instance_logs(instance_name: str, db: Session = Depends(get_db)) -> str:
    instance = InstanceModel.get_instance(db=db, instance_name=instance_name)
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return await Instance.from_orm(instance).logs()
