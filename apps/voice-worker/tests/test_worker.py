import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("INTERNAL_API_SECRET", "test-secret")
os.environ.setdefault("API_BASE_URL", "http://test")

from app.main import app  # noqa: E402
from app.tts_elevenlabs import ElevenLabsTTS  # noqa: E402
from app.config import Settings  # noqa: E402
from app.agent_loop import AgentLoop  # noqa: E402


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["service"] == "voice-worker"


@pytest.mark.asyncio
async def test_elevenlabs_tts_dev_fallback():
    settings = Settings(elevenlabs_api_key="")
    tts = ElevenLabsTTS(settings, voice_id="testVoice")
    frames = []
    async for f in tts.synthesize_mulaw_base64("Hello"):
        frames.append(f)
    assert len(frames) >= 1


@pytest.mark.asyncio
async def test_agent_heuristic_hours(monkeypatch):
    settings = Settings(openai_api_key="", api_base_url="http://unused")
    agent = AgentLoop(settings, "rest", "call", greeting="Hi")

    async def fake_call(name, args=None):
        if name == "get_hours":
            return {"ok": True, "result": {"hours": {"mon-sun": "11-22"}}}
        if name == "log_turn":
            return {"ok": True, "result": {}}
        return {"ok": True, "result": {}}

    monkeypatch.setattr(agent.tools, "call", fake_call)
    reply, action = await agent.handle_user_text("What are your hours?")
    assert "11-22" in reply or "hours" in reply.lower()
    assert action is None


@pytest.mark.asyncio
async def test_agent_transfer(monkeypatch):
    settings = Settings(openai_api_key="")
    agent = AgentLoop(settings, "rest", "call")

    async def fake_call(name, args=None):
        return {"ok": True, "result": {"transfer_number": "+1555"}}

    monkeypatch.setattr(agent.tools, "call", fake_call)
    reply, action = await agent.handle_user_text("Please transfer me to a human")
    assert action and action["tool"] == "transfer_to_staff"
    assert "staff" in reply.lower() or "transfer" in reply.lower()
