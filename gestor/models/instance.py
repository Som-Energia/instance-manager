from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from gestor.models.git import GitInfoModel
from gestor.schemas.instance import Instance
from gestor.utils.database import Base


class InstanceModel(Base):
    __tablename__ = "instances"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    name: Mapped[str] = mapped_column("name", nullable=False)
    git_info: Mapped["GitInfoModel"] = relationship(back_populates="instance")

    @classmethod
    def create_instance(cls, db: Session, instance: Instance):
        new_instance = cls(name=instance.name)
        db.add(new_instance)
        db.commit()
        db.refresh(new_instance)
        GitInfoModel.create_git_info(db, instance.git_info, new_instance.id)
        return new_instance

    @classmethod
    def get_instances(cls, db: Session):
        return db.query(cls).all()

    @classmethod
    def get_instance(cls, db: Session, instance_name: str):
        return db.query(cls).filter(cls.name == instance_name).first()
