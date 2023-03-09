from pydantic import BaseSettings


class Settings(BaseSettings):
    KUBERNETES_FILES_PATH: str
    TEMP_DIRECTORY_PATH: str
    DEPLOY_DOMAIN: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "GESTOR_"


settings = Settings()
