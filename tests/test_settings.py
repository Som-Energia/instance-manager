from config.test import TestingSettings


def test_import_testing_settings():
    from config import settings

    assert isinstance(settings, TestingSettings)
