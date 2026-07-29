"""Golden dialogues for the offline (heuristic) agent path.

These exercise reservation/menu/FAQ/transfer flows without OpenAI or ElevenLabs keys.
Speech synthesis still goes through ElevenLabsTTS (dev silence frames when key unset).
"""

import pytest

from app.agent_loop import AgentLoop
from app.config import Settings


@pytest.fixture
def settings():
    return Settings(openai_api_key="", elevenlabs_api_key="")


@pytest.mark.asyncio
async def test_golden_hours_then_goodbye(settings, monkeypatch):
    agent = AgentLoop(settings, "r1", "c1", greeting="Welcome!")
    calls = []

    async def fake_call(name, args=None):
        calls.append((name, args or {}))
        if name == "get_hours":
            return {"ok": True, "result": {"hours": {"daily": "11:00-22:00"}}}
        if name == "end_call":
            return {"ok": True, "result": {"action": "hangup"}}
        return {"ok": True, "result": {}}

    monkeypatch.setattr(agent.tools, "call", fake_call)
    greet = await agent.greet()
    assert "Welcome" in greet
    reply, _ = await agent.handle_user_text("Are you open? What are your hours?")
    assert "11:00-22:00" in reply
    reply2, action = await agent.handle_user_text("Goodbye")
    assert action and action["tool"] == "end_call"
    assert "goodbye" in reply2.lower() or "thanks" in reply2.lower()


@pytest.mark.asyncio
async def test_golden_menu_query(settings, monkeypatch):
    agent = AgentLoop(settings, "r1", "c1")

    async def fake_call(name, args=None):
        if name == "get_menu_item":
            return {
                "ok": True,
                "result": {
                    "items": [
                        {"name": "Margherita Pizza", "price_cents": 1400},
                        {"name": "Caesar Salad", "price_cents": 900},
                    ]
                },
            }
        return {"ok": True, "result": {}}

    monkeypatch.setattr(agent.tools, "call", fake_call)
    reply, _ = await agent.handle_user_text("What's on the menu for pizza?")
    assert "Margherita" in reply or "Caesar" in reply


@pytest.mark.asyncio
async def test_golden_reservation_prompt(settings, monkeypatch):
    agent = AgentLoop(settings, "r1", "c1")

    async def fake_call(name, args=None):
        return {"ok": True, "result": {}}

    monkeypatch.setattr(agent.tools, "call", fake_call)
    reply, _ = await agent.handle_user_text("I'd like to book a reservation")
    assert "party" in reply.lower() or "name" in reply.lower() or "table" in reply.lower()


@pytest.mark.asyncio
async def test_golden_faq_parking(settings, monkeypatch):
    agent = AgentLoop(settings, "r1", "c1")

    async def fake_call(name, args=None):
        if name == "search_faq":
            return {
                "ok": True,
                "result": {
                    "faqs": [
                        {
                            "question": "Do you have parking?",
                            "answer": "Street parking and a lot behind the restaurant.",
                        }
                    ]
                },
            }
        return {"ok": True, "result": {}}

    monkeypatch.setattr(agent.tools, "call", fake_call)
    reply, _ = await agent.handle_user_text("Is there parking nearby?")
    assert "parking" in reply.lower()
