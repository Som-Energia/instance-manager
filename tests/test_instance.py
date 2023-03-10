from config import settings
from gestor.schemas.git import GitInfo
from gestor.schemas.instance import Instance

test_git_info = GitInfo(
    commit="testtest",
    pull_request=1,
    branch="TEST_branch",
    repository="Som-Energia/test",
)

test_instance = Instance(
    git_info=test_git_info,
)


def test_computed_connection_parameters():
    expected_connection = test_instance.name + "." + settings.DEPLOY_DOMAIN
    assert expected_connection == test_instance.connection
