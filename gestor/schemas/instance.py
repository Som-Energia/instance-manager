import logging
from typing import Optional

import shortuuid
from pydantic import BaseModel, Field, validator

from config import settings
from gestor.schemas.git import GitInfo
from gestor.utils import kubernetes

_logger = logging.getLogger(__name__)


def instance_name():
    return "g" + shortuuid.uuid()[0:10].lower()


class Instance(BaseModel):
    name: str = Field(default_factory=instance_name)
    git_info: GitInfo
    connection: Optional[str]

    @validator("connection", pre=True, always=True)
    def make_connection(cls, _, values: dict):
        return values["name"] + "." + settings.DEPLOY_DOMAIN

    class Config:
        orm_mode = True

    async def deploy(self) -> None:
        _logger.info("Starting instance (%s)", str(self.dict()))
        data = {
            "name": self.name,
            "domain": settings.DEPLOY_DOMAIN,
            "labels": {},
            **self.git_info.dict(),
        }
        try:
            await kubernetes.new_deployment(self.name, data)
        except Exception as e:
            _logger.error("Failed to start the instance:%s", str(e))
            return
