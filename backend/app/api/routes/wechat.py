from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.core.config import get_settings
from app.integrations.wechat_crypto import WeChatCrypto, WeChatCryptoError


router = APIRouter()


@router.get("/callback", response_class=PlainTextResponse)
async def verify_callback(
    msg_signature: str = Query(...),
    timestamp: str = Query(...),
    nonce: str = Query(...),
    echostr: str = Query(...),
) -> str:
    settings = get_settings()
    crypto = WeChatCrypto(
        token=settings.wechat_token,
        encoding_aes_key=settings.wechat_aes_key,
        receive_id=settings.wechat_corp_id,
    )
    try:
        return crypto.verify_url(msg_signature, timestamp, nonce, echostr)
    except WeChatCryptoError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/callback")
async def receive_callback(request: Request) -> dict[str, str]:
    _ = await request.body()
    return {
        "status": "received",
        "message": "WeCom encrypted message handling will be implemented in Phase 3.",
    }
