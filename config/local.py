from config.base import Settings


class LocalSettings(Settings):
    class Config:
        env_file = ".env"


settings = LocalSettings()
