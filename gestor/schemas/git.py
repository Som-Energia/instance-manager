from pydantic import BaseModel


class GitInfo(BaseModel):
    commit: str
    repository: str
    pull_request: int
    branch: str

    class Config:
        orm_mode = True
