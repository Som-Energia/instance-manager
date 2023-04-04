import re
from unittest.mock import MagicMock

import pytest
from kubernetes.client import V1Deployment, V1ObjectMeta

from config import settings
from gestor.schemas.git import GitInfo
from gestor.schemas.instance import Instance
from gestor.utils import kubernetes

test_git_info = GitInfo(
    commit="testtest",
    pull_request=1,
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


def test_computed_connection_parameters():
    expected_connection = test_instance.name + "." + settings.DEPLOY_DOMAIN
    assert expected_connection == test_instance.connection


def test_default_factory_name():
    assert re.search("^g[a-z0-9]{11}$", test_instance.name)


@pytest.mark.asyncio
async def test_start_instance_kubernetes_exception(mocker):
    mocker.patch(
        "gestor.utils.kubernetes.start_deployment",
        side_effect=kubernetes.TemplateRenderFailed("Exception"),
    )
    magic_method = MagicMock()
    mocker.patch("gestor.schemas.instance._logger.error", magic_method)
    await test_instance.deploy()
    magic_method.assert_called_once()


@pytest.mark.asyncio
async def test_instance_from_deployment():
    instance_dict = await Instance.deployment_to_dict(test_deployment)
    instance = Instance.parse_obj(instance_dict)
    assert instance == test_instance
