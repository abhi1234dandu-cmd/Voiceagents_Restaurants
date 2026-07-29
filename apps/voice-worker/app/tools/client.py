from typing import Any

import httpx

from app.config import Settings


class ToolClient:
    def __init__(self, settings: Settings, restaurant_id: str, call_id: str):
        self.settings = settings
        self.restaurant_id = restaurant_id
        self.call_id = call_id

    async def call(self, name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {
            "restaurant_id": self.restaurant_id,
            "call_id": self.call_id,
            "args": args or {},
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                f"{self.settings.api_base_url}/internal/tools/{name}",
                json=payload,
                headers={"X-Internal-Secret": self.settings.internal_api_secret},
            )
            res.raise_for_status()
            return res.json()
