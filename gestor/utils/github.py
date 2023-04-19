import logging
from enum import Enum
from typing import Any

import aiohttp
from github import Github

from config import settings
from gestor.schemas.git import GitInfo

_logger = logging.getLogger(__name__)

# Do not show PyGitHub debug messages, too much verbose
logging.getLogger("github").setLevel(logging.INFO)

g = Github(login_or_token=settings.GITHUB_TOKEN)


class GitHubStatusState(str, Enum):
    error = "error"
    failure = "failure"
    pending = "pending"
    success = "success"


class InvalidGitHubUrl(Exception):
    pass


async def _github_request(path: str) -> Any:
    url = f"https://api.github.com{path}"

    _logger.debug("Fetching GitHub API (%s)", url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise InvalidGitHubUrl("GitHub URL not found (%s)" % url)
            return await response.json()


async def get_pull_request_info(repository: str, pull_request: int):
    _logger.debug(
        "Getting pull request information from GitHub API (%s/%d)",
        repository,
        pull_request,
    )
    path = f"/repos/{repository}/pulls/{pull_request}"
    try:
        pull_request_info = await _github_request(path)
    except InvalidGitHubUrl as e:
        raise e
    return GitInfo(
        repository=repository,
        pull_request=pull_request,
        commit=pull_request_info["head"]["sha"],
        branch=pull_request_info["head"]["ref"],
    )


async def get_branch_info(repository: str, branch: str):
    _logger.debug(
        "Getting branch information from GitHub API (%s/%s)",
        repository,
        branch,
    )
    path = f"/repos/{repository}/branches/{branch}"
    try:
        branch_info = await _github_request(path)
    except InvalidGitHubUrl as e:
        raise e

    return GitInfo(
        repository=repository,
        pull_request=None,
        commit=branch_info["commit"]["sha"],
        branch=branch,
    )


async def commit_exists(repository: str, commit: str) -> None:
    _logger.debug(
        "Getting commit information from GitHub API (%s/%s)",
        repository,
        commit,
    )
    path = f"/repos/{repository}/commits/{commit}"
    try:
        await _github_request(path)
    except InvalidGitHubUrl as e:
        raise e


async def set_commit_status(
    name: str, repository: str, commit: str, description: str, state: GitHubStatusState
):
    _logger.debug(
        "Setting commit %s status (%s)",
        commit,
        repository,
    )
    try:
        repo = g.get_repo(repository)
        commit = repo.get_commit(commit)
        commit.create_status(
            state=state,
            target_url="https://" + settings.DEPLOY_DOMAIN + "?name=" + name,
            description=description,
            context="instance-manager",
        )
    except Exception:
        _logger.error("Failed to set commit %s status (%s)", commit, repository)
