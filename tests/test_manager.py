from unittest.mock import AsyncMock

import pytest
from kubernetes.client import V1ObjectMeta, V1Deployment

from gestor import manager
from gestor.models.instance import InstanceModel
from gestor.schemas.git import GitInfo
from gestor.schemas.instance import Instance
from gestor.utils.database import Base, SessionLocal, engine

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

test_deployment = V1Deployment(
    api_version="apps/v1",
    kind="Deployment",
    metadata=V1ObjectMeta(
        name="test-deployment",
        labels={"gestor/name": test_instance.name},
        annotations={
            "gestor/branch": test_instance.git_info.branch,
            "gestor/commit": test_instance.git_info.commit,
            "gestor/pull_request": test_instance.git_info.pull_request,
            "gestor/repository": test_instance.git_info.repository,
        },
    ),
)

db = SessionLocal()


@pytest.mark.asyncio
async def test_create_instance_from_pull_request(mocker):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        return_value=test_git_info,
    )

    magic_method = AsyncMock()
    mocker.patch("gestor.schemas.instance.Instance.deploy", magic_method)
    await manager.manager.start_instance_from_pull_request("Som-Energia/test", 1)
    magic_method.assert_called_once()


@pytest.mark.asyncio
async def test_create_instance_from_pull_request_existing(mocker):
    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        return_value=test_git_info,
    )

    InstanceModel.create_instance(db, Instance(git_info=test_git_info))
    with pytest.raises(Exception) as e:
        await manager.manager.start_instance_from_pull_request("Som-Energia/fail", 1)


@pytest.mark.asyncio
async def test_init_db_from_cluster(mocker):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    mocker.patch(
        "gestor.utils.kubernetes.cluster_deployments",
        return_value=[test_deployment],
    )
    assert len(InstanceModel.get_instances(db)) == 0
    await manager.manager.init_db_from_cluster()
    db_instances = InstanceModel.get_instances(db)
    assert len(db_instances) == 1
    assert Instance.from_orm(db_instances[0]) == test_instance
