from pydantic import BaseSettings


class Settings(BaseSettings):
    KUBERNETES_FILES_PATH: str
    TEMP_DIRECTORY_PATH: str
    DEPLOY_DOMAIN: str
    API_TOKEN: str

    class Config:
        env_file_encoding = "utf-8"
        env_prefix = "GESTOR_"
