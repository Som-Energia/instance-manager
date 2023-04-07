from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from gestor.schemas.git import GitInfo, GitInfoFilter
from gestor.utils.database import Base


class GitInfoModel(Base):
    __tablename__ = "git_info"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )

    commit: Mapped[str] = mapped_column("commit", nullable=False)
    repository: Mapped[str] = mapped_column("repository", nullable=False)
    pull_request: Mapped[int] = mapped_column("pull_request", nullable=True)
    branch: Mapped[str] = mapped_column("branch", nullable=False)

    instance_id: Mapped[int] = mapped_column(ForeignKey("instances.id"))
    instance: Mapped["InstanceModel"] = relationship(back_populates="git_info")

    @classmethod
    def create_git_info(cls, db: Session, git_info: GitInfo, instance_id: int):
        db_git_info = cls(
            commit=git_info.commit,
            repository=git_info.repository,
            pull_request=git_info.pull_request,
            branch=git_info.branch,
            instance_id=instance_id,
        )
        db.add(db_git_info)
        db.commit()
        db.refresh(db_git_info)
        return db_git_info

    @classmethod
    def get_git_info_instance(cls, db: Session, git_info: GitInfoFilter):
        instance_git_info = (
            db.query(cls)
            .filter(
                cls.repository == git_info.repository,
                cls.pull_request == git_info.pull_request,
            )
            .first()
        )

        if instance_git_info:
            return instance_git_info.instance
        else:
            return None

    @classmethod
    def get_git_infos(cls, db: Session):
        return db.query(cls).all()
