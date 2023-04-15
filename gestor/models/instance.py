from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, Session, mapped_column

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
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime, nullable=False)
    commit: Mapped[str] = mapped_column("commit", nullable=False)
    repository: Mapped[str] = mapped_column("repository", nullable=False)
    pull_request: Mapped[int] = mapped_column("pull_request", nullable=True)
    branch: Mapped[str] = mapped_column("branch", nullable=True)

    @classmethod
    def create_instance(cls, db: Session, instance: Instance):
        if cls.get_instance(db, instance.name):
            return

        new_instance = cls(
            name=instance.name,
            server_port=instance.server_port,
            ssh_port=instance.ssh_port,
            is_ready=instance.is_ready,
            created_at=instance.created_at,
            commit=instance.git_info.commit,
            repository=instance.git_info.repository,
            pull_request=instance.git_info.pull_request,
            branch=instance.git_info.branch,
        )

        db.add(new_instance)
        db.commit()
        db.refresh(new_instance)

        return new_instance

    @classmethod
    def delete_instance(cls, db: Session, instance: Instance) -> None:
        db_instance = cls.get_instance(db, instance.name)
        if db_instance:
            db.delete(db_instance)
            db.commit()

    @classmethod
    def get_instances(
        cls, db: Session, name: str = None, repository: str = None, branch: str = None
    ):
        instance_query = db.query(cls)

        if name:
            instance_query = instance_query.filter(cls.name == name)
        if repository:
            instance_query = instance_query.filter(cls.repository == repository)
        if branch:
            instance_query = instance_query.filter(cls.branch == branch)

        return instance_query.all()

    @classmethod
    def get_instance(
        cls, db: Session, name: str = None, repository: str = None, branch: str = None
    ):
        instance_query = db.query(cls)

        if not name and not branch:
            return None

        if name:
            instance_query = instance_query.filter(cls.name == name)
        if repository:
            instance_query = instance_query.filter(cls.repository == repository)
        if branch:
            instance_query = instance_query.filter(cls.branch == branch)

        return instance_query.first()

    @classmethod
    def get_ports(cls, db: Session):
        return db.query(cls.server_port, cls.ssh_port).all()
