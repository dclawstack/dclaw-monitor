"""LLM abstraction layer. Tries OpenRouter first, falls back to Ollama."""
import json
import logging
from typing import AsyncGenerator

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def complete(prompt: str, system: str = "") -> str:
    """Non-streaming LLM completion. Tries OpenRouter, falls back to Ollama."""
    if settings.openrouter_api_key:
        try:
            return await _openrouter_complete(prompt, system)
        except Exception as e:
            logger.warning("OpenRouter failed, falling back to Ollama: %s", e)
    return await _ollama_complete(prompt, system)


async def stream_complete(prompt: str, system: str = "") -> AsyncGenerator[str, None]:
    """Streaming LLM completion. Tries OpenRouter SSE, falls back to Ollama."""
    if settings.openrouter_api_key:
        try:
            async for chunk in _openrouter_stream(prompt, system):
                yield chunk
            return
        except Exception as e:
            logger.warning("OpenRouter streaming failed, falling back to Ollama: %s", e)
    async for chunk in _ollama_stream(prompt, system):
        yield chunk


def _build_messages(prompt: str, system: str) -> list[dict]:
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    return msgs


async def _openrouter_complete(prompt: str, system: str) -> str:
    messages = _build_messages(prompt, system)
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={"model": settings.llm_model, "messages": messages},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _openrouter_stream(prompt: str, system: str) -> AsyncGenerator[str, None]:
    messages = _build_messages(prompt, system)
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={"model": settings.llm_model, "messages": messages, "stream": True},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                line = line.strip()
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    delta = data["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue


async def _ollama_complete(prompt: str, system: str) -> str:
    messages = _build_messages(prompt, system)
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/chat",
            json={"model": settings.ollama_model, "messages": messages, "stream": False},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]


async def _ollama_stream(prompt: str, system: str) -> AsyncGenerator[str, None]:
    messages = _build_messages(prompt, system)
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{settings.ollama_base_url}/api/chat",
            json={"model": settings.ollama_model, "messages": messages, "stream": True},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
                    if data.get("done"):
                        break
                except (json.JSONDecodeError, KeyError):
                    continue
