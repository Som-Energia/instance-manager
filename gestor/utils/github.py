from typing import Any

import aiohttp

from gestor.schemas.git import GitInfo


async def _github_request(path: str) -> Any:
    url = f"https://api.github.com{path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 404:
                raise Exception("GitHub URL not found")
            return await response.json()


async def get_info_from_pull_request(repository: str, pull_request: int):
    path = f"/repos/{repository}/pulls/{pull_request}"
    pull_request_info = await _github_request(path)
    return GitInfo(
        repository=repository,
        pull_request=pull_request,
        commit=pull_request_info["head"]["sha"],
        branch=pull_request_info["head"]["ref"],
    )
