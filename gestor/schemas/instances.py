from pydantic import BaseModel


class InstanceBase(BaseModel):
    commit: str
    repository: str
    pull_request: int


class InstanceCreate(InstanceBase):
    pass


class Instance(InstanceBase):
    id: int

    class Config:
        orm_mode = True
