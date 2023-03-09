import shortuuid
from pydantic import BaseModel, Field

from gestor.schemas.git import GitInfo


def instance_name():
    return "g" + shortuuid.uuid()[:-1].lower()


class InstanceBase(BaseModel):
    name: str = Field(default_factory=instance_name)
    git_info: GitInfo


class Instance(InstanceBase):
    class Config:
        orm_mode = True
