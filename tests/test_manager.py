import pytest

from gestor import manager
from gestor.models.instance import InstanceModel
from gestor.schemas.git import GitInfo
from gestor.schemas.instance import Instance
from gestor.utils.database import SessionLocal, engine, Base

test_git_info = GitInfo(
    commit="testtest",
    pull_request=1,
    branch="TEST_branch",
    repository="Som-Energia/test",
)

test_git_info_2 = GitInfo(
    commit="testtest",
    pull_request=2,
    branch="TEST_branch",
    repository="Som-Energia/test",
)

test_instance = Instance(
    git_info=test_git_info,
)

db = SessionLocal()


@pytest.mark.asyncio
async def test_create_instance_from_pull_request(mocker):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    mocker.patch(
        "gestor.schemas.instance.Instance.deploy",
        return_value=None,
    )
    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        return_value=test_git_info,
    )

    # New instance
    await manager.manager.start_instance_from_pull_request("Som-Energia/test", 1)
    assert len(InstanceModel.get_instances(db)) == 1

    # Existing instance
    await manager.manager.start_instance_from_pull_request("Som-Energia/test", 1)
    assert len(InstanceModel.get_instances(db)) == 1

    # Different new instance
    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        return_value=test_git_info_2,
    )
    await manager.manager.start_instance_from_pull_request("Som-Energia/test", 2)
    assert len(InstanceModel.get_instances(db)) == 2
