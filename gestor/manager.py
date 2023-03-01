from gestor.utils.github import get_commit_from_pull_request
from gestor.schemas.instances import InstanceCreate


class Manager:
    async def deploy(self, instance: InstanceCreate) -> None:
        pass

    async def deploy_pull_request(self, repository: str, pull_request: int) -> None:
        commit = await get_commit_from_pull_request(repository, pull_request)
        instance = InstanceCreate(
            commit=commit,
            repository=repository,
            pull_request=pull_request,
        )
        await self.deploy(instance)


manager = Manager()
