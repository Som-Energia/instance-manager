import hashlib
import hmac
import logging

from fastapi import APIRouter, Request, Header

from config import settings

router = APIRouter()

_logger = logging.getLogger(__name__)


def _verify_signature(payload_body: bytes, secret_token: str, signature_header: str):
    if not signature_header:
        _logger.warning("x-hub-signature-256 header is missing!")
        return False
    hash_object = hmac.new(
        bytes(secret_token, "utf-8"), msg=payload_body, digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        _logger.warning("Request signatures didn't match!")
        return False
    return True


@router.get("/")
async def root():
    return {"message": "Hello Webhooks!"}


@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_hub_signature_256: str | None = Header(None),
):
    body = await request.body()
    return _verify_signature(body, settings.WEBHOOKS_SECRET, x_hub_signature_256)
