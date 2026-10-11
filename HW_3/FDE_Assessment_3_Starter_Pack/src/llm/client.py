from __future__ import annotations

import os

import requests

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_DECISION_URL = "https://openrouter.ai/api/alpha/decisions"
DEFAULT_TIMEOUT = 15.0


def call_openrouter(
    model: str,
    messages: list[dict[str, str]],
    reasoning_effort: str | None = None,
    json_mode: bool = False,
) -> dict[str, object] | None:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    headers: dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "AI Procurement Request Copilot",
    }

    payload: dict[str, object] = {
        "model": model,
        "messages": messages,
    }

    if reasoning_effort is not None:
        payload["reasoning"] = {"effort": reasoning_effort}

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = requests.post(
            OPENROUTER_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )
        if response.status_code == 200:
            data: dict[str, object] = response.json()
            return data
    except requests.RequestException:
        pass
    return None


def call_openrouter_decisions(
    model: str,
    state: dict[str, str],
    questions: dict[str, object],
) -> dict[str, object] | None:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    headers: dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "AI Procurement Request Copilot",
    }

    payload: dict[str, object] = {
        "model": model,
        "state": state,
        "questions": questions,
    }

    try:
        response = requests.post(
            OPENROUTER_DECISION_URL,
            headers=headers,
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )
        if response.status_code == 200:
            data: dict[str, object] = response.json()
            return data
    except requests.RequestException:
        pass
    return None
