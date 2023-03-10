import logging
from typing import Optional

import shortuuid
from pydantic import BaseModel, Field, validator

from config import settings
from gestor.schemas.git import GitInfo


def instance_name():
    return "g" + shortuuid.uuid()[0:10].lower()


class InstanceBase(BaseModel):
    name: str = Field(default_factory=instance_name)
    git_info: GitInfo
    connection: Optional[str]

    @validator("connection", pre=True, always=True)
    def make_connection(cls, _, values: dict):
        return values["name"] + "." + settings.DEPLOY_DOMAIN

class Instance(InstanceBase):
    class Config:
        orm_mode = True
