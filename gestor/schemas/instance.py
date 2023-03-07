import shortuuid
from pydantic import BaseModel, Field

from gestor.schemas.git import GitInfo


class InstanceBase(BaseModel):
    name: str = Field(default_factory=shortuuid.uuid)
    git_info: GitInfo


class InstanceCreate(InstanceBase):
    pass


class Instance(InstanceBase):
    id: int

    class Config:
        orm_mode = True
