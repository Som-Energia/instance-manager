from sqlalchemy import Boolean, Column, Integer, String
from gestor.utils.database import Base


class Instance(Base):
    __tablename__ = "instances"

    id = Column(Integer, primary_key=True, index=True)
    repository = Column(String)
    pull_request = Column(Integer)
    is_active = Column(Boolean, default=True)
