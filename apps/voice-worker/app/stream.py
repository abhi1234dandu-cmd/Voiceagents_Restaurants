import asyncio
import base64
import json
from typing import Any, Optional

from fastapi import WebSocket, WebSocketDisconnect

from app.agent_loop import AgentLoop
from app.config import Settings
from app.stt_openai import SpeechToText
from app.tts_elevenlabs import ElevenLabsTTS

# Active stream counter for autoscaling signals
ACTIVE_STREAMS = 0


async def handle_media_stream(websocket: WebSocket, settings: Settings) -> None:
    """Twilio Media Stream handler.

    Pipeline: STT (OpenAI Whisper) → LLM+tools (OpenAI) → TTS (ElevenLabs streaming).
    Per-call voice_id comes from voice_agents via Twilio custom parameters.
    """
    global ACTIVE_STREAMS
    await websocket.accept()
    ACTIVE_STREAMS += 1
    stream_sid: Optional[str] = None
    call_id = ""
    restaurant_id = ""
    agent: Optional[AgentLoop] = None
    tts: Optional[ElevenLabsTTS] = None
    stt = SpeechToText(settings)
    audio_buffer = bytearray()
    started = asyncio.get_event_loop().time()

    try:
        while True:
            if asyncio.get_event_loop().time() - started > settings.max_call_seconds:
                break
            message = await websocket.receive_text()
            data = json.loads(message)
            event = data.get("event")

            if event == "start":
                stream_sid = data.get("streamSid") or data.get("start", {}).get("streamSid")
                custom = data.get("start", {}).get("customParameters", {})
                call_id = custom.get("call_id", "")
                restaurant_id = custom.get("restaurant_id", "")
                voice_id = custom.get("voice_id") or settings.elevenlabs_default_voice_id
                greeting = custom.get("greeting") or "Thanks for calling. How can I help?"
                system_prompt = custom.get("system_prompt") or ""
                agent = AgentLoop(
                    settings,
                    restaurant_id,
                    call_id,
                    greeting=greeting,
                    system_prompt=system_prompt,
                )
                tts = ElevenLabsTTS(settings, voice_id=voice_id)
                greet_text = await agent.greet()
                await _speak(websocket, stream_sid, tts, greet_text)

            elif event == "media" and agent and tts:
                payload = data.get("media", {}).get("payload", "")
                if payload:
                    audio_buffer.extend(base64.b64decode(payload))
                # Simple VAD-ish flush: every ~20KB treat as utterance end for MVP testability
                if len(audio_buffer) > 20000:
                    text = stt.transcribe_mulaw(bytes(audio_buffer))
                    audio_buffer.clear()
                    if text:
                        reply, action = await agent.handle_user_text(text)
                        await _speak(websocket, stream_sid, tts, reply)
                        if action and action.get("tool") == "transfer_to_staff":
                            await websocket.send_text(
                                json.dumps({"event": "clear", "streamSid": stream_sid})
                            )
                            break
                        if action and action.get("tool") == "end_call":
                            break

            elif event == "mark":
                pass

            elif event == "stop":
                break

            # Test/dev injection: custom text event for golden dialogue tests
            elif event == "user_text" and agent and tts:
                reply, action = await agent.handle_user_text(data.get("text", ""))
                await websocket.send_text(
                    json.dumps({"event": "assistant_text", "text": reply, "action": action})
                )
                await _speak(websocket, stream_sid or "MZ", tts, reply)
                if action and action.get("tool") in ("transfer_to_staff", "end_call"):
                    break

    except WebSocketDisconnect:
        pass
    finally:
        ACTIVE_STREAMS = max(0, ACTIVE_STREAMS - 1)
        try:
            await websocket.close()
        except Exception:
            pass


async def _speak(
    websocket: WebSocket, stream_sid: Optional[str], tts: ElevenLabsTTS, text: str
) -> None:
    """Always synthesize via ElevenLabs (mulaw frames for Twilio)."""
    if not stream_sid:
        stream_sid = "MZ_dev"
    async for frame_b64 in tts.synthesize_mulaw_base64(text):
        await websocket.send_text(
            json.dumps(
                {
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {"payload": frame_b64},
                }
            )
        )
    await websocket.send_text(
        json.dumps({"event": "mark", "streamSid": stream_sid, "mark": {"name": "tts_done"}})
    )


def concurrency_stats() -> dict[str, Any]:
    return {"active_streams": ACTIVE_STREAMS}
