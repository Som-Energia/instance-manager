from pydantic import BaseSettings


class Settings(BaseSettings):
    KUBERNETES_FILES_PATH: str
    KUBERNETES_NAMESPACE: str
    TEMP_DIRECTORY_PATH: str
    DEPLOY_DOMAIN: str
    SSH_IP: str
    SSH_USER: str
    SSH_KEY_PATH: str
    ALLOWED_REPOSITORIES: list[str]
    LIMIT_INSTANCES: bool
    WEBHOOKS_SECRET: str
    GITHUB_TOKEN: str

    class Config:
        env_file_encoding = "utf-8"
        env_prefix = "GESTOR_"
