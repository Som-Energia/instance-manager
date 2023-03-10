import logging
import os
import shutil
import subprocess

from kubernetes import client, config
from kubernetes.client import V1Deployment
from mako.template import Template

from config import settings

_logger = logging.getLogger(__name__)


class TemporaryDirectoryNotFound(Exception):
    pass


class TemplateRenderFailed(Exception):
    pass


def get_api_client():
    config.load_kube_config()
    return client.AppsV1Api()


async def _kubectl(args: list[str]) -> int:
    """Executes a kubectl command"""
    _logger.info("kubectl %s", " ".join(args))
    result = subprocess.run(["kubectl", *args])
    return result.returncode


async def _create_working_directory(name: str) -> str:
    if not os.path.exists(settings.TEMP_DIRECTORY_PATH):
        raise TemporaryDirectoryNotFound(
            "Temporary directory path does not exist:%s" % settings.TEMP_DIRECTORY_PATH
        )

    working_directory_path = os.path.join(settings.TEMP_DIRECTORY_PATH, name)
    os.mkdir(working_directory_path)
    shutil.copytree(
        settings.KUBERNETES_FILES_PATH, working_directory_path, dirs_exist_ok=True
    )
    _logger.info("Copied Kubernetes files to %s", working_directory_path)

    return working_directory_path


async def _render_kubernetes_file(directory_path: str, data=None) -> str:
    """Generates Kubernetes files using data parameter"""
    # Render Mako template and store output
    if data is None:
        data = {}

    kustomization_template = Template(
        filename=os.path.join(directory_path, "kustomization.mako")
    )
    try:
        output = kustomization_template.render(**data)
    except Exception as e:
        raise TemplateRenderFailed(
            "Could not render kustomization file from Mako template:%s" % str(e)
        )

    # Write output to file
    output_file_path = os.path.join(directory_path, "kustomization.yaml")
    with open(output_file_path, "w") as f:
        f.write(output)
    _logger.info("Kustomization file render saved (%s)", output_file_path)

    return output_file_path


async def new_deployment(name: str, data: dict = {}) -> None:
    """Starts a new deployment in the Kubernetes cluster"""
    _logger.info("Deploying %s", name)
    tmp_dir_path = await _create_working_directory(name)
    await _render_kubernetes_file(tmp_dir_path, data)
    await _kubectl(["apply", "-k", tmp_dir_path])


async def cluster_deployments() -> list[V1Deployment]:
    """Starts a new deployment in the Kubernetes cluster"""
    return get_api_client().list_namespaced_deployment(namespace="default").items
