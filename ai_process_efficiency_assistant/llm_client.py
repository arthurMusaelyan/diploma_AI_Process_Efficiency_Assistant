"""OpenAI client with mock fallback for the Streamlit MVP."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import dotenv_values, load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    OpenAIError,
    PermissionDeniedError,
    RateLimitError,
)


PROJECT_DIR = Path(__file__).resolve().parent
ENV_PATH = PROJECT_DIR / ".env"

PLACEHOLDER_KEYS = {
    "your_openai_api_key_here",
    "твій_ключ_без_лапок",
    "your_key_here",
    "sk-your-key-here",
}


def load_config() -> dict[str, Any]:
    """Load runtime configuration from .env next to app.py."""

    if ENV_PATH.exists():
        env_values = dotenv_values(ENV_PATH)
        api_key = str(env_values.get("OPENAI_API_KEY") or "").strip()
        model = str(env_values.get("OPENAI_MODEL") or "gpt-4o-mini").strip()
        app_mode = str(env_values.get("APP_MODE") or "auto").strip().lower()
    else:
        load_dotenv(override=True)
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        app_mode = os.getenv("APP_MODE", "auto").strip().lower()

    model = model or "gpt-4o-mini"
    app_mode = app_mode or "auto"

    if app_mode not in {"auto", "real", "mock"}:
        app_mode = "mock"

    key_is_placeholder = api_key in PLACEHOLDER_KEYS

    return {
        "api_key": api_key,
        "model": model,
        "app_mode": app_mode,
        "env_path": ENV_PATH,
        "env_exists": ENV_PATH.exists(),
        "key_present": bool(api_key),
        "key_is_placeholder": key_is_placeholder,
        "has_real_api_key": bool(api_key) and not key_is_placeholder,
    }


def _masked_key(api_key: str) -> str:
    if not api_key:
        return "not set"
    if api_key in PLACEHOLDER_KEYS:
        return "placeholder value"
    if len(api_key) <= 12:
        return "detected, too short to preview safely"
    return f"{api_key[:7]}****"


def get_config_status() -> dict[str, Any]:
    """Return debug-safe OpenAI configuration status for the UI."""

    config = load_config()
    return {
        "env_path": str(config["env_path"]),
        "env_exists": config["env_exists"],
        "app_mode": config["app_mode"],
        "model": config["model"],
        "key_detected": config["key_present"],
        "key_is_placeholder": config["key_is_placeholder"],
        "key_preview": _masked_key(config["api_key"]),
        "runtime_mode": get_runtime_mode(),
        "real_api_available": config["has_real_api_key"]
        and config["app_mode"] in {"auto", "real"},
    }


def _has_real_api_key(config: dict[str, Any]) -> bool:
    return bool(config["has_real_api_key"])


def is_real_api_available() -> bool:
    config = load_config()
    return _has_real_api_key(config) and config["app_mode"] in ["auto", "real"]


def get_runtime_mode() -> str:
    config = load_config()
    app_mode = config["app_mode"]

    if app_mode == "mock":
        return "mock"
    if app_mode == "real":
        return "real" if _has_real_api_key(config) else "real_missing_key"
    if app_mode == "auto":
        return "real" if _has_real_api_key(config) else "missing_key"
    return "mock"


def ask_llm_text(
    system_prompt: str,
    user_prompt: str,
    max_output_tokens: int = 1200,
) -> dict[str, Any]:
    """Send a text request to OpenAI and return a source-aware result."""

    mode = get_runtime_mode()
    config = load_config()

    if mode == "real_missing_key":
        return _error_result(
            "missing_api_key",
            "OPENAI_API_KEY is missing. Please add it to your .env file.",
            mode,
        )

    if mode in {"mock", "missing_key"}:
        return _mock_result(mode)

    try:
        client = OpenAI(api_key=config["api_key"])
        response = client.responses.create(
            model=config["model"],
            instructions=system_prompt,
            input=user_prompt,
            temperature=0.2,
            max_output_tokens=max_output_tokens,
        )
        return {
            "ok": True,
            "source": "openai",
            "runtime_mode": mode,
            "data": response.output_text,
            "error": None,
            "error_type": None,
        }
    except Exception as exc:
        return _openai_error_result(exc, mode)


def ask_llm_json(
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any],
    max_output_tokens: int = 1500,
) -> dict[str, Any]:
    """Send a structured JSON request to OpenAI and return a source-aware result."""

    mode = get_runtime_mode()
    config = load_config()

    if mode == "real_missing_key":
        return _error_result(
            "missing_api_key",
            "OPENAI_API_KEY is missing. Please add it to your .env file.",
            mode,
        )

    if mode in {"mock", "missing_key"}:
        return _mock_result(mode)

    try:
        client = OpenAI(api_key=config["api_key"])
        response = client.responses.create(
            model=config["model"],
            instructions=system_prompt,
            input=user_prompt,
            temperature=0.2,
            max_output_tokens=max_output_tokens,
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema.get("name", "response_schema"),
                    "schema": schema["schema"],
                    "strict": True,
                }
            },
        )
        return {
            "ok": True,
            "source": "openai",
            "runtime_mode": mode,
            "data": json.loads(response.output_text),
            "error": None,
            "error_type": None,
        }
    except json.JSONDecodeError as exc:
        return _error_result(
            "json_parsing_error",
            f"OpenAI response was not valid JSON: {exc}",
            mode,
        )
    except Exception as exc:
        return _openai_error_result(exc, mode)


def test_openai_connection() -> dict[str, Any]:
    """Send exactly one small request for manual connection testing."""

    return ask_llm_text(
        "You are a connection test. Follow the user instruction exactly.",
        "Reply exactly: OpenAI connection works.",
        max_output_tokens=30,
    )


def _mock_result(mode: str) -> dict[str, Any]:
    return {
        "ok": False,
        "source": "mock",
        "runtime_mode": mode,
        "data": None,
        "error": (
            "Mock mode is active. Add a valid OPENAI_API_KEY to .env to get real AI analysis."
        ),
        "error_type": "mock_mode",
    }


def _error_result(error_type: str, message: str, mode: str) -> dict[str, Any]:
    return {
        "ok": False,
        "source": "error",
        "runtime_mode": mode,
        "data": None,
        "error": message,
        "error_type": error_type,
    }


def _openai_error_result(exc: Exception, mode: str) -> dict[str, Any]:
    if isinstance(exc, AuthenticationError):
        return _error_result("invalid_api_key", f"Invalid API key: {exc}", mode)
    if isinstance(exc, PermissionDeniedError):
        return _error_result("permission_denied", f"OpenAI permission error: {exc}", mode)
    if isinstance(exc, RateLimitError):
        message = str(exc)
        lower_message = message.lower()
        if "insufficient_quota" in lower_message or "quota" in lower_message:
            return _error_result(
                "insufficient_quota",
                f"OpenAI quota or billing issue: {exc}",
                mode,
            )
        return _error_result("rate_limit", f"OpenAI rate limit error: {exc}", mode)
    if isinstance(exc, APITimeoutError):
        return _error_result("api_timeout", f"OpenAI API timeout: {exc}", mode)
    if isinstance(exc, APIConnectionError):
        return _error_result("api_connection_error", f"OpenAI connection error: {exc}", mode)
    if isinstance(exc, BadRequestError):
        return _error_result("bad_request", f"OpenAI bad request error: {exc}", mode)
    if isinstance(exc, APIStatusError):
        return _error_result(
            "api_request_error",
            f"OpenAI API status error {exc.status_code}: {exc}",
            mode,
        )
    if isinstance(exc, OpenAIError):
        return _error_result("api_request_error", f"OpenAI API error: {exc}", mode)
    return _error_result("api_request_error", f"OpenAI API call failed: {exc}", mode)


def mock_text_response(user_prompt: str) -> str:
    return "Mock mode is active. Add a valid OPENAI_API_KEY to .env to get real AI analysis."


def mock_json_response(user_prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    return _mock_result(get_runtime_mode())
