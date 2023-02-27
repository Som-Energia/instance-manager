from sqlalchemy.orm import Session

from gestor.models.instances import Instance
from gestor.schemas.instances import InstanceCreate


def create_instance(db: Session, instance: InstanceCreate):
    db_instance = Instance(
        repository=instance.repository,
        pull_request=instance.pull_request,
    )
    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)
    return db_instance


def get_instances(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Instance).offset(skip).limit(limit).all()


def get_instance(db: Session, instance_id: int):
    return db.query(Instance).filter(Instance.id == instance_id).first()


def search_instance(db: Session, repository: str, pull_request: int):
    return (
        db.query(Instance)
        .filter(
            Instance.repository == repository,
            Instance.pull_request == pull_request,
        )
        .first()
    )
