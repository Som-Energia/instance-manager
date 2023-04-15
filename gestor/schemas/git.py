from typing import Optional

from pydantic import BaseModel


class GitInfoFilter(BaseModel):
    repository: str
    branch: str


class GitInfo(GitInfoFilter):
    commit: str
    repository: str
    pull_request: Optional[int]
    branch: Optional[str]

    class Config:
        orm_mode = True
