from pydantic import BaseModel

from gestor.schemas.git import GitInfo


class InstanceBase(BaseModel):
    git_info: GitInfo


class InstanceCreate(InstanceBase):
    pass


class Instance(InstanceBase):
    id: int

    class Config:
        orm_mode = True
