import json

import pytest

from gestor.schemas.git import GitInfo
from gestor.utils import github

test_response = json.loads(
    """
    {
        "url": "https://api.github.com/repos/Som-Energia/test/pulls/1",
        "created_at": "2023-03-03T12:09:42Z",
        "updated_at": "2023-03-03T12:35:40Z",
        "closed_at": null,
        "merged_at": null,
        "head": {
            "label": "Som-Energia:TEST_branch",
            "ref": "TEST_branch",
            "sha": "testtest"
        }
    }
    """,
    strict=False,
)


@pytest.mark.asyncio
async def test_get_information_from_pull_request(mocker):
    mocker.patch("gestor.utils.github._github_request", return_value=test_response)

    expected_git_info = GitInfo(
        commit="testtest",
        pull_request=1,
        branch="TEST_branch",
        repository="Som-Energia/test",
    )
    assert (
        await github.get_pull_request_info("Som-Energia/test", 1) == expected_git_info
    )


@pytest.mark.asyncio
async def test_get_information_from_pull_request_not_found(mocker):
    mocker.patch(
        "gestor.utils.github._github_request",
        side_effect=github.InvalidGitHubUrl("Exception"),
    )
    with pytest.raises(github.InvalidGitHubUrl) as e:
        await github.get_pull_request_info("Som-Energia/test", 1)
    assert str(e.value) == "Exception"


@pytest.mark.asyncio
async def test__github_request():
    with pytest.raises(github.InvalidGitHubUrl):
        await github._github_request("/test-invalid-url")
