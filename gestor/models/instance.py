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
    server_port: Mapped[int] = mapped_column("server_port", nullable=False)
    ssh_port: Mapped[int] = mapped_column("ssh_port", nullable=False)
    is_ready: Mapped[bool] = mapped_column("is_ready", nullable=False)
    git_info: Mapped["GitInfoModel"] = relationship(
        back_populates="instance", cascade="all, delete-orphan"
    )

    @classmethod
    def create_instance(cls, db: Session, instance: Instance):
        if cls.get_instance(db, instance.name):
            return

        new_instance = cls(
            name=instance.name,
            server_port=instance.server_port,
            ssh_port=instance.ssh_port,
            is_ready=instance.is_ready,
        )

        db.add(new_instance)
        db.commit()
        db.refresh(new_instance)
        GitInfoModel.create_git_info(db, instance.git_info, new_instance.id)
        return new_instance

    @classmethod
    def delete_instance(cls, db: Session, instance: Instance) -> None:
        db_instance = cls.get_instance(db, instance.name)
        if db_instance:
            db.delete(db_instance)
            db.commit()

    @classmethod
    def get_instances(cls, db: Session):
        return db.query(cls).all()

    @classmethod
    def get_instance(cls, db: Session, instance_name: str):
        return db.query(cls).filter(cls.name == instance_name).first()

    @classmethod
    def get_ports(cls, db: Session):
        return db.query(cls.server_port, cls.ssh_port).all()
