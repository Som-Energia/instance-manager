import aiohttp


async def _github_request(path: str) -> str:
    url = f"https://api.github.com{path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 404:
                raise Exception("GitHub URL not found")
            return await response.json()


async def get_commit_from_pull_request(repository: str, pull_request: int):
    path = f"/repos/{repository}/pulls/{pull_request}"
    pull_request_info = await _github_request(path)
    return pull_request_info["head"]["sha"]
