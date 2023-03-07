from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from gestor.models.git import GitInfoModel, create_git_info
from gestor.schemas.instance import InstanceCreate
from gestor.schemas.git import GitInfo, GitInfoFilter
from gestor.utils.database import Base


class InstanceModel(Base):
    __tablename__ = "instances"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    name: Mapped[str] = mapped_column("name", nullable=False)
    git_info: Mapped["GitInfoModel"] = relationship(back_populates="instance")


def create_instance(db: Session, instance: InstanceCreate):
    new_instance = InstanceModel(name=instance.name)
    db.add(new_instance)
    db.commit()
    db.refresh(new_instance)
    create_git_info(db, instance.git_info, new_instance.id)
    return new_instance


def get_instances(db: Session):
    return db.query(InstanceModel).all()


def get_instance(db: Session, instance_name: str):
    return db.query(InstanceModel).filter(InstanceModel.name == instance_name).first()


def get_instance_by_git_info(db: Session, git_info: GitInfoFilter):
    instance_git_info = (
        db.query(GitInfoModel)
        .filter(
            GitInfoModel.repository == git_info.repository,
            GitInfoModel.pull_request == git_info.pull_request,
            GitInfoModel.branch == git_info.branch,
        )
        .first()
    )

    if instance_git_info:
        return instance_git_info.instance
    else:
        return None
