from pydantic import BaseModel


class GitInfoFilter(BaseModel):
    repository: str
    pull_request: int


class GitInfo(GitInfoFilter):
    commit: str
    repository: str
    pull_request: int
    branch: str

    class Config:
        orm_mode = True
