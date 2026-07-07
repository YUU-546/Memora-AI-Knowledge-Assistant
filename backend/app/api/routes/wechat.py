from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/callback")
async def verify_callback() -> dict[str, str]:
    return {
        "status": "pending",
        "message": "WeCom callback verification will be implemented in Phase 3.",
    }


@router.post("/callback")
async def receive_callback(request: Request) -> dict[str, str]:
    _ = await request.body()
    return {
        "status": "received",
        "message": "WeCom encrypted message handling will be implemented in Phase 3.",
    }
