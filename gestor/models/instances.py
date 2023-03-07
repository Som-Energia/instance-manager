from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from gestor.models.git import GitInfoModel, create_git_info
from gestor.schemas.instances import InstanceCreate
from gestor.utils.database import Base


class InstanceModel(Base):
    __tablename__ = "instances"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    git_info: Mapped["GitInfoModel"] = relationship(back_populates="instance")


def create_instance(db: Session, instance: InstanceCreate):
    db_instance = InstanceModel()
    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)
    create_git_info(db, instance.git_info, db_instance.id)
    return db_instance


def get_instances(db: Session):
    return db.query(InstanceModel).all()


def get_instance(db: Session, instance_id: int):
    return db.query(InstanceModel).filter(InstanceModel.id == instance_id).first()
