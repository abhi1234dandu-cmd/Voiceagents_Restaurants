import json
import time
from pathlib import Path
from typing import Any, Optional

from app.config import Settings
from app.tools.client import ToolClient
from app.tools.specs import TOOL_SPECS


def load_system_prompt(extra: str = "") -> str:
    base = (Path(__file__).parent / "prompts" / "system.txt").read_text(encoding="utf-8")
    return f"{base}\n{extra}".strip()


class AgentLoop:
    def __init__(
        self,
        settings: Settings,
        restaurant_id: str,
        call_id: str,
        greeting: str = "Thanks for calling. How can I help?",
        system_prompt: str = "",
    ):
        self.settings = settings
        self.tools = ToolClient(settings, restaurant_id, call_id)
        self.greeting = greeting
        self.messages: list[dict[str, Any]] = [
            {"role": "system", "content": load_system_prompt(system_prompt)},
        ]
        self._client = None
        self.failure_count = 0

    @property
    def client(self):
        if self._client is None and self.settings.openai_api_key:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    async def greet(self) -> str:
        await self.tools.call("log_turn", {"role": "assistant", "content": self.greeting})
        return self.greeting

    async def handle_user_text(self, text: str) -> tuple[str, Optional[dict[str, Any]]]:
        """Returns (assistant_speech, optional_control_action)."""
        started = time.time()
        await self.tools.call("log_turn", {"role": "user", "content": text})
        self.messages.append({"role": "user", "content": text})

        if not self.client:
            # Deterministic offline agent for tests / local without OpenAI
            reply, action = await self._heuristic(text)
            latency = int((time.time() - started) * 1000)
            await self.tools.call(
                "log_turn",
                {"role": "assistant", "content": reply, "latency_ms": latency, "tool_name": (action or {}).get("tool")},
            )
            return reply, action

        try:
            completion = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=self.messages,
                tools=TOOL_SPECS,
                tool_choice="auto",
            )
            msg = completion.choices[0].message
            action = None
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments or "{}")
                    result = await self.tools.call(name, args)
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(result),
                        }
                    )
                    if name in ("transfer_to_staff", "end_call"):
                        action = {"tool": name, "result": result}
                follow = self.client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=self.messages,
                )
                reply = follow.choices[0].message.content or "Okay."
            else:
                reply = msg.content or "Okay."
            self.messages.append({"role": "assistant", "content": reply})
            self.failure_count = 0
        except Exception:
            self.failure_count += 1
            if self.failure_count >= 2:
                action = {"tool": "transfer_to_staff"}
                reply = "I'm having trouble with that. Let me connect you to the restaurant staff."
                await self.tools.call("transfer_to_staff", {})
            else:
                reply = "Sorry, could you say that again?"
                action = None

        latency = int((time.time() - started) * 1000)
        await self.tools.call("log_turn", {"role": "assistant", "content": reply, "latency_ms": latency})
        return reply, action

    async def _heuristic(self, text: str) -> tuple[str, Optional[dict[str, Any]]]:
        lower = text.lower()
        if "hour" in lower or "open" in lower:
            result = await self.tools.call("get_hours", {})
            return f"Our hours are {json.dumps(result.get('result', {}).get('hours', {}))}.", None
        if "menu" in lower or "price" in lower:
            result = await self.tools.call("get_menu_item", {"query": text})
            items = result.get("result", {}).get("items", [])
            if not items:
                return "I couldn't find that on the menu. Anything else?", None
            names = ", ".join(i.get("name", "") for i in items[:3])
            return f"I found: {names}.", None
        if "reserv" in lower or "book" in lower or "table" in lower:
            return (
                "I'd be happy to book a table. What name, party size, and date and time should I use?",
                None,
            )
        if "transfer" in lower or "human" in lower or "manager" in lower:
            result = await self.tools.call("transfer_to_staff", {})
            return "Transferring you to the staff now.", {"tool": "transfer_to_staff", "result": result}
        if "bye" in lower or "goodbye" in lower:
            await self.tools.call("end_call", {"outcome": "completed"})
            return "Thanks for calling. Goodbye!", {"tool": "end_call"}
        # FAQ fallback
        result = await self.tools.call("search_faq", {"query": text})
        faqs = result.get("result", {}).get("faqs", [])
        if faqs:
            return faqs[0].get("answer", "Okay."), None
        # Embeddings retrieval path
        result = await self.tools.call("embed_search", {"query": text})
        faqs = result.get("result", {}).get("faqs", [])
        if faqs:
            return faqs[0].get("answer", "Okay."), None
        return "I can help with hours, menu questions, or reservations. What do you need?", None
