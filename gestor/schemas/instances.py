from pydantic import BaseModel


class InstanceBase(BaseModel):
    repository: str
    pull_request: int


class InstanceCreate(InstanceBase):
    pass


class Instance(InstanceBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
