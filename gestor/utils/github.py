import logging
from typing import Any

import aiohttp

from gestor.schemas.git import GitInfo

_logger = logging.getLogger(__name__)


class InvalidGitHubUrl(Exception):
    pass


async def _github_request(path: str) -> Any:
    url = f"https://api.github.com{path}"

    _logger.info("Fetching GitHub API (%s)", url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 404:
                raise InvalidGitHubUrl("GitHub URL not found (%s)" % url)
            return await response.json()


async def get_pull_request_info(repository: str, pull_request: int):
    _logger.info(
        "Getting pull request information from GitHub API (%s/%d)",
        repository,
        pull_request,
    )
    path = f"/repos/{repository}/pulls/{pull_request}"
    pull_request_info = await _github_request(path)
    return GitInfo(
        repository=repository,
        pull_request=pull_request,
        commit=pull_request_info["head"]["sha"],
        branch=pull_request_info["head"]["ref"],
    )
