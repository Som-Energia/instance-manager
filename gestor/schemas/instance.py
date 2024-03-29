import datetime
import logging
import random

import shortuuid
from kubernetes.client import V1Deployment
from pydantic import BaseModel, Field

from config import settings
from gestor.schemas.git import GitInfo
from gestor.utils import kubernetes

_logger = logging.getLogger(__name__)


def instance_name():
    return "g" + shortuuid.uuid()[0:11].lower()


def server_port():
    return random.randint(30000, 32767)


def ssh_port():
    return random.randint(30000, 32767)


class Instance(BaseModel):
    name: str = Field(default_factory=instance_name)
    git_info: GitInfo
    server_port: int = Field(default_factory=server_port)
    ssh_port: int = Field(default_factory=ssh_port)
    is_ready = False
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, instance: any):
        return cls(
            name=instance.name,
            server_port=instance.server_port,
            ssh_port=instance.ssh_port,
            is_ready=instance.is_ready,
            created_at=instance.created_at,
            git_info=GitInfo(
                pull_request=instance.pull_request,
                commit=instance.commit,
                repository=instance.repository,
                branch=instance.branch,
            ),
        )

    async def deploy(self, target_module: str = None) -> None:
        _logger.info("Starting instance (%s)", str(self.dict()))
        data = {
            "name": self.name,
            "server_port": self.server_port,
            "ssh_port": self.ssh_port,
            "created_at": self.created_at,
            "domain": settings.DEPLOY_DOMAIN,
            "labels": {},
            **self.git_info.dict(),
        }
        if target_module:
            data["target_module"] = target_module
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
            return "Failed to get logs"

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
        is_ready = (
            deployment.status.replicas == deployment.status.ready_replicas
            and deployment.status.ready_replicas == 1
        )

        if annotations["pull_request"] == "None":
            annotations["pull_request"] = None
        if annotations["branch"] == "None":
            annotations["branch"] = None
        return {"git_info": annotations, "is_ready": is_ready, **labels, **annotations}
