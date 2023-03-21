import logging
from asyncio import create_task, Queue

from kubernetes.client import V1Deployment

from gestor.models.git import GitInfoModel
from gestor.models.instance import InstanceModel
from gestor.schemas.instance import Instance
from gestor.utils import github
from gestor.utils import kubernetes
from gestor.utils.database import SessionLocal

_logger = logging.getLogger(__name__)


class Manager:
    def __init__(self):
        self._db = SessionLocal()
        self._tasks = []

    async def start_instance_from_pull_request(
        self, repository: str, pull_request: int
    ) -> None:
        try:
            git_info = await github.get_pull_request_info(repository, pull_request)
        except github.InvalidGitHubUrl as e:
            _logger.error("Error getting pull request information:%s" % str(e))
            return

        # Allow just one instance for a repository pull_request
        instance = GitInfoModel.get_git_info_instance(self._db, git_info)
        if instance:
            _logger.error(
                "An instance for %s/%d already exists:%s",
                repository,
                pull_request,
                instance.name,
            )
            return
        instance = Instance(git_info=git_info)
        await instance.deploy()

    async def init_db_from_cluster(self):
        deployments = await kubernetes.cluster_deployments()
        for deployment in deployments:
            instance = Instance.parse_obj(await self.deployment_to_dict(deployment))
            InstanceModel.create_instance(self._db, instance)
            InstanceModel.create_instance(self._db, instance)

    @staticmethod
    async def watch_kubernetes_events(event_queue):
        await kubernetes.watch_deployments(event_queue)

    async def process_kubernetes_events(self, event_queue):
        while True:
            event = await event_queue.get()
            event_type = event["type"]
            deployment = event["object"]
            _logger.debug("Event %s %s", event_type, deployment.metadata.name)
            instance = Instance.parse_obj(await self.deployment_to_dict(deployment))
            try:
                if event_type == "ADDED":
                    InstanceModel.create_instance(self._db, instance)
                elif event_type == "DELETED":
                    InstanceModel.delete_instance(self._db, instance)
            except Exception:
                pass

    async def start(self) -> None:
        event_queue = Queue()
        self._tasks.append(create_task(self.init_db_from_cluster()))
        self._tasks.append(create_task(self.watch_kubernetes_events(event_queue)))
        self._tasks.append(create_task(self.process_kubernetes_events(event_queue)))

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


manager = Manager()
