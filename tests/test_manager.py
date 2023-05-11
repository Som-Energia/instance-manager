from unittest.mock import AsyncMock

import pytest
from kubernetes.client import V1ObjectMeta, V1Deployment, V1DeploymentStatus

from gestor import manager
from gestor.models.instance import InstanceModel
from gestor.schemas.git import GitInfo
from gestor.schemas.instance import Instance
from gestor.utils import github
from gestor.utils.database import Base, SessionLocal, engine

test_git_info = GitInfo(
    commit="testtest",
    pull_request=1,
    branch="TEST_branch",
    repository="Som-Energia/openerp_som_addons",
)

test_git_info_2 = GitInfo(
    commit="testtest",
    pull_request=2,
    branch="TEST_branch",
    repository="Som-Energia/openerp_som_addons",
)

test_git_info_3 = GitInfo(
    commit="testtesttest",
    pull_request=2,
    branch="TEST_branch",
    repository="Som-Energia/openerp_som_addons",
)

test_git_info_not_allowed = GitInfo(
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
            "gestor/server_port": test_instance.server_port,
            "gestor/ssh_port": test_instance.ssh_port,
            "gestor/created_at": test_instance.created_at,
        },
    ),
    status=V1DeploymentStatus(
        ready_replicas=1,
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
    await manager.manager.start_instance_from_pull_request(
        "Som-Energia/openerp_som_addons", 1
    )
    magic_method.assert_called_once()


@pytest.mark.asyncio
async def test_create_instance_from_pull_request_not_allowed(mocker):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        return_value=test_git_info,
    )

    with pytest.raises(Exception) as e:
        await manager.manager.start_instance_from_pull_request("Som-Energia/fail", 1)


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
async def test_create_instance_from_pull_request_github_fail(mocker):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        side_effect=github.InvalidGitHubUrl("Exception"),
    )

    with pytest.raises(Exception) as e:
        await manager.manager.start_instance_from_pull_request(
            "Som-Energia/openerp_som_addons", 1
        )


@pytest.mark.asyncio
async def test_create_instance_from_webhook(mocker):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        return_value=test_git_info,
    )

    magic_method = AsyncMock()
    mocker.patch("gestor.schemas.instance.Instance.deploy", magic_method)
    await manager.manager.start_instance_from_webhook(test_git_info)
    magic_method.assert_called_once()


@pytest.mark.asyncio
async def test_create_instance_from_webhook_not_allowed(mocker):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        return_value=test_git_info_not_allowed,
    )

    magic_method = AsyncMock()
    mocker.patch("gestor.schemas.instance.Instance.deploy", magic_method)
    await manager.manager.start_instance_from_webhook(test_git_info_not_allowed)
    magic_method.assert_not_called()


@pytest.mark.asyncio
async def test_create_instance_from_webhook_existing(mocker):
    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        return_value=test_git_info,
    )

    InstanceModel.create_instance(db, Instance(git_info=test_git_info))
    magic_method = AsyncMock()
    mocker.patch("gestor.schemas.instance.Instance.deploy", magic_method)
    await manager.manager.start_instance_from_webhook(test_git_info)
    magic_method.assert_not_called()


@pytest.mark.asyncio
async def test_create_instance_from_webhook_limit(mocker):
    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        return_value=test_git_info_3,
    )

    InstanceModel.create_instance(db, Instance(git_info=test_git_info_2))
    magic_method_deploy = AsyncMock()
    mocker.patch("gestor.schemas.instance.Instance.deploy", magic_method_deploy)
    magic_method_undeploy = AsyncMock()
    mocker.patch("gestor.schemas.instance.Instance.undeploy", magic_method_undeploy)
    await manager.manager.start_instance_from_webhook(test_git_info_3)
    magic_method_deploy.assert_called_once()
    magic_method_undeploy.assert_called_once()


@pytest.mark.asyncio
async def test_start_instance_limit():
    InstanceModel.create_instance(db, Instance(git_info=test_git_info_2))
    with pytest.raises(Exception) as e:
        await manager.manager.start_instance(Instance(git_info=test_git_info_3))


@pytest.mark.asyncio
async def test_create_instance_from_branch(mocker):
    mocker.patch(
        "gestor.utils.github.get_branch_info",
        return_value=test_git_info,
    )

    magic_method = AsyncMock()
    mocker.patch("gestor.manager.Manager.start_instance", magic_method)
    await manager.manager.start_instance_from_branch(
        "Som-Energia/openerp_som_addons", "TEST_branch", "TEST"
    )
    magic_method.assert_called_once()


@pytest.mark.asyncio
async def test_create_instance_from_branch_not_allowed(mocker):
    magic_method = AsyncMock()
    mocker.patch("gestor.manager.Manager.start_instance", magic_method)
    with pytest.raises(Exception) as e:
        await manager.manager.start_instance_from_branch(
            "Som-Energia/test", "TEST_branch", "TEST"
        )
    magic_method.assert_not_called()


@pytest.mark.asyncio
async def test_create_instance_from_branch_github_fail(mocker):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    mocker.patch(
        "gestor.utils.github.get_branch_info",
        side_effect=github.InvalidGitHubUrl("Exception"),
    )

    with pytest.raises(Exception) as e:
        await manager.manager.start_instance_from_branch(
            "Som-Energia/openerp_som_addons", "TEST_branch", "TEST"
        )


@pytest.mark.asyncio
async def test_create_instance_from_commit(mocker):
    mocker.patch(
        "gestor.utils.github.commit_exists",
        return_value=test_git_info,
    )
    mocker.patch(
        "gestor.utils.github._github_request",
        return_value="ok",
    )
    magic_method = AsyncMock()
    mocker.patch("gestor.manager.Manager.start_instance", magic_method)
    await manager.manager.start_instance_from_commit(
        "Som-Energia/openerp_som_addons", "testtest", "TEST"
    )
    magic_method.assert_called_once()


@pytest.mark.asyncio
async def test_create_instance_from_commit_not_allowed(mocker):
    magic_method = AsyncMock()
    mocker.patch("gestor.manager.Manager.start_instance", magic_method)
    with pytest.raises(Exception) as e:
        await manager.manager.start_instance_from_commit(
            "Som-Energia/test", "testtest", "TEST"
        )
    magic_method.assert_not_called()


@pytest.mark.asyncio
async def test_create_instance_from_commit_github_fail(mocker):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    mocker.patch(
        "gestor.utils.github.get_pull_request_info",
        side_effect=github.InvalidGitHubUrl("Exception"),
    )

    with pytest.raises(Exception) as e:
        await manager.manager.start_instance_from_commit(
            "Som-Energia/openerp_som_addons", "testtest", "TEST"
        )


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
