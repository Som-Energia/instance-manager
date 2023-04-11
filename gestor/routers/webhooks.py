import hashlib
import hmac
import logging

from fastapi import APIRouter, Request, Header, BackgroundTasks

from config import settings
from gestor.manager import manager
from gestor.schemas.git import GitInfo

router = APIRouter()

_logger = logging.getLogger(__name__)


def _verify_signature(payload_body: bytes, secret_token: str, signature_header: str):
    if not signature_header:
        _logger.warning("x-hub-signature-256 header is missing")
        return False
    hash_object = hmac.new(
        bytes(secret_token, "utf-8"), msg=payload_body, digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        _logger.warning("Request signatures didn't match")
        return False
    return True


@router.get("/")
async def root():
    return {"message": "Hello Webhooks!"}


@router.post("/github")
async def github_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
    x_github_event: str = Header(...),
    x_hub_signature_256: str | None = Header(None),
):
    body = await request.body()
    if False and not _verify_signature(
        body, settings.WEBHOOKS_SECRET, x_hub_signature_256
    ):
        return
    if x_github_event != "pull_request":
        return
    payload = await request.json()
    git_info = GitInfo(
        repository=payload["pull_request"]["head"]["repo"]["full_name"],
        pull_request=payload["pull_request"]["number"],
        commit=payload["pull_request"]["head"]["sha"],
        branch=payload["pull_request"]["head"]["ref"],
    )
    if payload["action"] in [
        "open",
        "synchronize",
    ]:  # new pull request or new commits pushed
        background_tasks.add_task(manager.start_instance_from_webhook, git_info)
    elif payload["action"] == "closed":  # pull request closed
        background_tasks.add_task(manager.stop_instance_from_webhook, git_info)
