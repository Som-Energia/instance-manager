import logging
from asyncio import create_task, Queue, gather

from config import settings
from gestor.models.git import GitInfoModel
from gestor.models.instance import InstanceModel
from gestor.schemas.git import GitInfo
from gestor.schemas.instance import Instance
from gestor.utils import github
from gestor.utils import kubernetes
from gestor.utils.database import SessionLocal
from gestor.utils.github import set_commit_status, GitHubStatusState

_logger = logging.getLogger(__name__)


class Manager:
    def __init__(self):
        self._db = SessionLocal()
        self._tasks = []

    async def stop_instance_from_webhook(self, git_info: GitInfo) -> None:
        if git_info.repository not in settings.ALLOWED_REPOSITORIES:
            _logger.debug("Repository %s is not allowed", git_info.repository)
            return

        existing_instance = GitInfoModel.get_git_info_instance(self._db, git_info)

        if existing_instance:
            _logger.debug(
                "Stopping instance %s PR%d:%s",
                existing_instance.git_info.repository,
                existing_instance.git_info.pull_request,
                existing_instance.name,
            )
            instance = Instance.from_orm(existing_instance)
            await instance.undeploy()
        else:
            _logger.debug(
                "Instance not found %s PR%d",
                git_info.repository,
                git_info.pull_request,
            )

    async def start_instance_from_webhook(self, git_info: GitInfo) -> None:
        if git_info.repository not in settings.ALLOWED_REPOSITORIES:
            _logger.debug("Repository %s is not allowed", git_info.repository)
            return

        existing_instance = GitInfoModel.get_git_info_instance(self._db, git_info)

        if existing_instance and existing_instance.git_info.commit == git_info.commit:
            return

        if existing_instance and settings.LIMIT_INSTANCES:
            _logger.debug(
                "An instance for %s/%s already exists, it will we replaced:%s",
                existing_instance.git_info.repository,
                existing_instance.git_info.branch,
                existing_instance.name,
            )
            instance = Instance.from_orm(existing_instance)
            await instance.undeploy()

        instance = Instance(git_info=git_info)
        await instance.deploy()

    async def start_instance(self, instance: Instance, module: str = None):
        # Allow just one instance for a repository branch
        existing_instance = GitInfoModel.get_git_info_instance(
            self._db, instance.git_info
        )

        if existing_instance and settings.LIMIT_INSTANCES:
            _logger.debug(
                "An instance for %s/%s already exists:%s",
                instance.git_info.repository,
                instance.git_info.branch,
                instance.name,
            )
            raise Exception("An instance for the associated branch already exists")

        await instance.deploy(module)

    async def start_instance_from_pull_request(
        self, repository: str, pull_request: int
    ) -> None:
        if repository not in settings.ALLOWED_REPOSITORIES:
            raise Exception("This repository is not allowed")
        try:
            git_info = await github.get_pull_request_info(repository, pull_request)
        except github.InvalidGitHubUrl as e:
            _logger.debug("Error getting pull request information:%s" % str(e))
            raise Exception("Error getting pull request information")

        instance = Instance(git_info=git_info)
        await self.start_instance(instance)

    async def start_instance_from_branch(
        self, repository: str, branch: str, module: str
    ) -> None:
        if repository not in settings.ALLOWED_REPOSITORIES:
            raise Exception("This repository is not allowed")
        try:
            git_info = await github.get_branch_info(repository, branch)
        except github.InvalidGitHubUrl as e:
            _logger.debug("Error getting branch information:%s" % str(e))
            raise Exception("Error getting branch information")

        instance = Instance(git_info=git_info)
        await self.start_instance(instance, module)

    async def init_db_from_cluster(self):
        deployments = await kubernetes.cluster_deployments()
        for deployment in deployments:
            instance = Instance.parse_obj(await Instance.deployment_to_dict(deployment))
            InstanceModel.create_instance(self._db, instance)
            InstanceModel.create_instance(self._db, instance)

    async def process_kubernetes_events(self, event_queue):
        while True:
            event = await event_queue.get()
            event_type = event["type"]
            deployment = event["object"]
            _logger.debug("Event %s %s", event_type, deployment.metadata.name)
            instance = Instance.parse_obj(await Instance.deployment_to_dict(deployment))
            try:
                if event_type == "ADDED":
                    InstanceModel.create_instance(self._db, instance)
                elif event_type == "DELETED":
                    InstanceModel.delete_instance(self._db, instance)
                elif event_type == "MODIFIED":
                    InstanceModel.delete_instance(self._db, instance)
                    InstanceModel.create_instance(self._db, instance)
                await self.update_commit_status(instance, event_type)
            except Exception:
                pass

    async def start(self) -> None:
        event_queue = Queue()
        self._tasks.append(create_task(self.init_db_from_cluster()))
        self._tasks.append(create_task(self.watch_kubernetes_events(event_queue)))
        self._tasks.append(create_task(self.process_kubernetes_events(event_queue)))

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        await gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    @staticmethod
    async def watch_kubernetes_events(event_queue):
        await kubernetes.watch_deployments(event_queue)

    @staticmethod
    async def update_commit_status(instance: Instance, event: str) -> None:
        if not instance.git_info.pull_request:
            return
        if event == "DELETED":
            await set_commit_status(
                instance.git_info.repository,
                instance.git_info.commit,
                "The instance no longer exists",
                GitHubStatusState.failure,
            )
            return
        if event not in ["ADDED", "MODIFIED"]:  # Invalid events
            return
        if event == "MODIFIED" and not instance.is_ready:  # Avoid unnecessary API calls
            return
        if instance.is_ready:
            await set_commit_status(
                instance.git_info.repository,
                instance.git_info.commit,
                "The instance is ready",
                GitHubStatusState.success,
            )
        else:
            await set_commit_status(
                instance.git_info.repository,
                instance.git_info.commit,
                "The instance is initializing",
                GitHubStatusState.pending,
            )


manager = Manager()
