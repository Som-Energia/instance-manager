import logging

from config import settings
from gestor.models.git import GitInfoModel
from gestor.models.instance import InstanceModel
from gestor.schemas.instance import Instance
from gestor.utils import github, kubernetes
from gestor.utils.database import SessionLocal

_logger = logging.getLogger(__name__)


async def start_instance(instance: Instance) -> None:
    _logger.info("Starting instance (%s)", str(instance.dict()))
    data = {
        "name": instance.name,
        "domain": settings.DEPLOY_DOMAIN,
        "labels": {},
        **instance.git_info.dict(),
    }
    try:
        await kubernetes.new_deployment(instance.name, data)
    except Exception as e:
        _logger.error("Failed to start the instance:%s", str(e))
        return


class Manager:
    db = SessionLocal()

    @classmethod
    async def start_pr_instance(cls, repository: str, pull_request: int) -> None:
        try:
            git_info = await github.get_pull_request_info(repository, pull_request)
        except github.InvalidGitHubUrl as e:
            _logger.error("Error getting pull request information:%s" % str(e))
            return

        # Allow just one instance for a repository pull_request
        instance = GitInfoModel.get_git_info_instance(cls.db, git_info)
        if instance:
            # TODO: Check for new commits and update
            _logger.error(
                "An instance for %s/%d already exists:%s",
                repository,
                pull_request,
                instance.name,
            )
            return

        # Create and start a new instance
        instance = Instance.from_orm(
            InstanceModel.create_instance(cls.db, Instance(git_info=git_info))
        )
        await start_instance(instance)


manager = Manager()
