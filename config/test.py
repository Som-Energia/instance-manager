from config.base import Settings


class TestingSettings(Settings):
    __test__ = False

    class Config:
        env_file = ".env.test"


settings = TestingSettings()
