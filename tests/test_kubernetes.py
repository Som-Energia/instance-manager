import os

import pytest

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


@pytest.mark.asyncio
async def test__create_working_directory_ok():
    test_instance = Instance(git_info=test_git_info)
    working_directory_path = await kubernetes._create_working_directory(
        test_instance.name
    )
    expected_path = os.path.join(settings.TEMP_DIRECTORY_PATH, test_instance.name)
    assert expected_path == working_directory_path
    assert os.path.exists(working_directory_path)


@pytest.mark.asyncio
async def test__create_working_directory_no_tmp(mocker):
    test_instance = Instance(git_info=test_git_info)
    mocker.patch(
        "os.path.exists",
        return_value=False,
    )
    with pytest.raises(Exception):
        await kubernetes._create_working_directory(test_instance.name)


@pytest.mark.asyncio
async def test__render_kubernetes_file_ok():
    test_instance = Instance(git_info=test_git_info)
    data = {
        "name": test_instance.name,
        "domain": settings.DEPLOY_DOMAIN,
        "labels": {},
        **test_instance.git_info.dict(),
    }
    working_directory_path = await kubernetes._create_working_directory(
        test_instance.name
    )

    await kubernetes._render_kubernetes_file(working_directory_path, data)
    expected_file_path = os.path.join(working_directory_path, "kustomization.yaml")

    assert os.path.isfile(expected_file_path)


@pytest.mark.asyncio
async def test__render_kubernetes_file_missing_data():
    test_instance = Instance(git_info=test_git_info)
    data = {
        "name": test_instance.name,
        "labels": {},
        **test_instance.git_info.dict(),
    }
    working_directory_path = await kubernetes._create_working_directory(
        test_instance.name
    )

    with pytest.raises(Exception):
        await kubernetes._render_kubernetes_file(working_directory_path, data)
    expected_file_path = os.path.join(working_directory_path, "kustomization.yaml")
    assert not os.path.isfile(expected_file_path)
