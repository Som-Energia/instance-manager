import logging
from typing import Optional

import shortuuid
from kubernetes.client import V1Deployment
from pydantic import BaseModel, Field, validator

from config import settings
from gestor.schemas.git import GitInfo
from gestor.utils import kubernetes

_logger = logging.getLogger(__name__)


def instance_name():
    return "g" + shortuuid.uuid()[0:11].lower()


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
            await kubernetes.start_deployment(self.name, data)
        except Exception as e:
            _logger.error("Failed to start the instance:%s", str(e))

    async def undeploy(self) -> None:
        _logger.info("Removing instance (%s)", str(self.dict()))
        try:
            await kubernetes.remove_deployment(self.name)
        except Exception as e:
            _logger.error("Failed to remove the instance:%s", str(e))

    async def logs(self) -> str:
        try:
            return await kubernetes.pod_logs(self.name)
        except Exception as e:
            _logger.error("Failed to get instance logs:%s", str(e))
            return "Failed"

    @staticmethod
    async def deployment_to_dict(deployment: V1Deployment):
        annotations = {
            key.replace("gestor/", ""): value
            for key, value in deployment.metadata.annotations.items()
        }
        labels = {
            key.replace("gestor/", ""): value
            for key, value in deployment.metadata.labels.items()
        }
        return {"git_info": annotations, **labels}
