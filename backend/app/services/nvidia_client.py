"""NVIDIA NIM LLM client.

NVIDIA's hosted inference endpoint is OpenAI-API compatible, so we use the
`openai` SDK pointed at the NVIDIA base URL. This module is the single gateway
through which every AI pipeline (classification, summarization, RAG, analysis)
talks to an LLM — keeping prompt/transport concerns out of the services.
"""
from __future__ import annotations

import json
from typing import Any

from loguru import logger
from openai import APIError, AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.exceptions import ConfigurationError, ExternalServiceError


class NvidiaLLMClient:
    """Async wrapper around the NVIDIA NIM chat-completions endpoint."""

    def __init__(self) -> None:
        if not settings.nvidia_api_key:
            # Real-calls-only policy: fail clearly rather than silently mocking.
            raise ConfigurationError(
                "NVIDIA_API_KEY is not set. The LLM pipelines require a valid "
                "NVIDIA NIM key — get one free at https://build.nvidia.com"
            )
        self._client = AsyncOpenAI(
            api_key=settings.nvidia_api_key,
            base_url=settings.nvidia_base_url,
        )

    @retry(
        retry=retry_if_exception_type((APIError, ExternalServiceError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        reraise=True,
    )
    async def complete(
        self,
        *,
        system: str,
        user: str,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> str:
        """Run a single-turn chat completion and return the text content."""
        model = model or settings.nvidia_llm_model
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature
            if temperature is not None
            else settings.nvidia_temperature,
            "max_tokens": max_tokens or settings.nvidia_max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            resp = await self._client.chat.completions.create(**kwargs)
        except APIError as exc:
            logger.error("NVIDIA API error ({}): {}", model, exc)
            raise ExternalServiceError(f"NVIDIA inference failed: {exc}") from exc

        content = resp.choices[0].message.content or ""
        logger.debug("NVIDIA completion ok | model={} | chars={}", model, len(content))
        return content.strip()

    async def complete_chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Multi-turn chat completion (used by the conversational chat service)."""
        model = model or settings.nvidia_llm_model
        try:
            resp = await self._client.chat.completions.create(
                model=model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature
                if temperature is not None
                else settings.nvidia_temperature,
                max_tokens=max_tokens or settings.nvidia_max_tokens,
            )
        except APIError as exc:
            logger.error("NVIDIA chat error ({}): {}", model, exc)
            raise ExternalServiceError(f"NVIDIA inference failed: {exc}") from exc
        return (resp.choices[0].message.content or "").strip()

    async def complete_json(
        self, *, system: str, user: str, model: str | None = None
    ) -> dict[str, Any]:
        """Run a completion expected to return JSON and parse it defensively."""
        raw = await self.complete(
            system=system, user=user, model=model, json_mode=True, temperature=0.1
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Some models wrap JSON in prose/markdown fences — extract the object.
            start, end = raw.find("{"), raw.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(raw[start : end + 1])
                except json.JSONDecodeError:
                    pass
            logger.warning("Failed to parse JSON from LLM output: {}", raw[:200])
            raise ExternalServiceError("LLM returned malformed JSON")


_client: NvidiaLLMClient | None = None


def get_llm_client() -> NvidiaLLMClient:
    """Lazily-instantiated singleton LLM client (FastAPI dependency-friendly)."""
    global _client
    if _client is None:
        _client = NvidiaLLMClient()
    return _client
