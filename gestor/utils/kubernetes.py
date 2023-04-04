import asyncio
import logging
import os
import shutil
import subprocess
from typing import cast

from kubernetes.client import V1Deployment, V1Pod
from kubernetes_asyncio import config, watch, client
from kubernetes_asyncio.client.api_client import ApiClient
from mako.template import Template

from config import settings

_logger = logging.getLogger(__name__)


class TemporaryDirectoryNotFound(Exception):
    pass


class TemplateRenderFailed(Exception):
    pass


async def _kubectl(args: list[str]) -> int:
    """Executes a kubectl command"""
    _logger.info("kubectl %s", " ".join(args))
    result = subprocess.run(["kubectl", *args])
    return result.returncode


async def _create_working_directory(name: str) -> str:
    if not os.path.exists(settings.TEMP_DIRECTORY_PATH):
        try:
            os.mkdir(settings.TEMP_DIRECTORY_PATH)
        except Exception:
            raise TemporaryDirectoryNotFound(
                "Temporary directory path does not exist:%s"
                % settings.TEMP_DIRECTORY_PATH
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


async def start_deployment(name: str, data: dict = None) -> None:
    """Starts a new deployment in the Kubernetes cluster"""
    if data is None:
        data = {}
    _logger.info("Deploying %s", name)
    tmp_dir_path = await _create_working_directory(name)
    await _render_kubernetes_file(tmp_dir_path, data)
    await _kubectl(["apply", "-k", tmp_dir_path])


async def remove_deployment(name: str) -> None:
    """Removes a deployment in the Kubernetes cluster"""
    _logger.info("Undeploying %s", name)
    await _kubectl(["delete", "deployment", name + "-erpserver-deployment"])
    await _kubectl(["delete", "ingress", name + "-erpserver"])
    await _kubectl(["delete", "service", name + "-erpserver"])


async def pod_logs(name: str) -> str:
    async with ApiClient() as api:
        v1 = client.CoreV1Api(api)
        pods = await v1.list_namespaced_pod(
            namespace="default", label_selector="gestor/name={}".format(name)
        )
        if pods.items:
            return cast(
                str,
                await v1.read_namespaced_pod_log(
                    name=pods.items[0].metadata.name,
                    namespace="default",
                    container="erpserver",
                    tail_lines=None,
                    follow=False,
                ),
            )
        else:
            raise Exception("Pod not found in the cluster")


async def cluster_deployments() -> list[V1Deployment]:
    """Starts a new deployment in the Kubernetes cluster"""
    async with ApiClient() as api:
        v1 = client.AppsV1Api(api)
        deployments = await v1.list_namespaced_deployment(namespace="default")
        return deployments.items


async def cluster_pods() -> list[V1Pod]:
    """Starts a new deployment in the Kubernetes cluster"""
    async with ApiClient() as api:
        v1 = client.AppsV1Api(api)
        deployments = await v1.list_namespaced_deployment(namespace="default")
        return deployments.items


async def watch_deployments(event_queue):
    await config.load_kube_config()
    async with ApiClient() as api:
        v1 = client.AppsV1Api(api)
        deployment_watcher = watch.Watch()
        async with deployment_watcher.stream(
            v1.list_namespaced_deployment, namespace="default"
        ) as s:
            while True:
                try:
                    event = await asyncio.wait_for(s.__anext__(), timeout=None)
                    await event_queue.put(event)
                except asyncio.TimeoutError:
                    pass
