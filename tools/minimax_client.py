"""Minimal MiniMax client for the War365 tooling.

Auth resolution, in order:

1. Environment. ``MINIMAX_API_KEY`` is the server path: a key from the
   MiniMax platform, dropped into an EnvironmentFile such as
   ``/etc/war365/minimax.env``. ``MINIMAX_BASE_URL`` overrides the endpoint
   and ``MINIMAX_AUTH_STYLE`` picks the header (bearer or x-api-key).
2. The local MiniMax Code runtime. The provider baseURL comes from its
   ``config.yaml`` and the session token from ``local-runtime.auth.json``.
   This is the desktop path, and it is how the tooling is tested locally.

Both the platform API and the runtime proxy speak the Anthropic messages
protocol, but they differ in endpoint shape and in what they will accept
about thinking, so the call tries a small set of request variants and keeps
the first one that works.

Stdlib only. Nothing is written to disk and no credential is ever printed.
"""

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

PLATFORM_BASE_URL = "https://api.minimax.io/anthropic"
DEFAULT_MODEL = "MiniMax-M3.1-Flash"


class MiniMaxError(Exception):
    pass


def _data_dir() -> Path:
    for var in ("__MAVIS_PARENT_DATA_DIR", "MINIMAX_DATA_DIR"):
        val = os.environ.get(var)
        if val:
            return Path(val)
    return Path.home() / ".minimax"


def _runtime_base_url() -> str | None:
    path = Path(os.environ.get("MINIMAX_CONFIG", _data_dir() / "config.yaml"))
    if not path.exists():
        return None
    m = re.search(r"baseURL:\s*(\S+)", path.read_text(encoding="utf-8"))
    return m.group(1).strip("'\"") if m else None


def _runtime_model() -> str | None:
    path = Path(os.environ.get("MINIMAX_CONFIG", _data_dir() / "config.yaml"))
    if not path.exists():
        return None
    m = re.search(r"defaultModel:\s*(\S+)", path.read_text(encoding="utf-8"))
    return m.group(1).strip("'\"") if m else None


def _runtime_token() -> str | None:
    path = Path(
        os.environ.get("MINIMAX_RUNTIME_AUTH", _data_dir() / "local-runtime.auth.json")
    )
    if not path.exists():
        return None
    try:
        auth = json.loads(path.read_text(encoding="utf-8")).get("auth", {})
    except (ValueError, OSError):
        return None
    return auth.get("accessToken") or None


def resolve_auth() -> tuple[str, str, str]:
    """Return (base_url, credential, auth_style)."""
    style = os.environ.get("MINIMAX_AUTH_STYLE", "bearer").strip().lower()
    if style not in ("bearer", "x-api-key"):
        style = "bearer"

    key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("MINIMAX_AUTH_TOKEN")
    if key:
        base = os.environ.get("MINIMAX_BASE_URL", "").strip() or (
            PLATFORM_BASE_URL if not os.environ.get("MINIMAX_BASE_URL") else ""
        )
        if not base:
            base = PLATFORM_BASE_URL
        return base.rstrip("/"), key, style

    base = os.environ.get("MINIMAX_BASE_URL", "").strip() or _runtime_base_url()
    token = _runtime_token()
    if base and token:
        return base.rstrip("/"), token, style

    raise MiniMaxError(
        "No MiniMax credential found. Set MINIMAX_API_KEY in the environment, "
        "or run on a machine with the MiniMax Code runtime installed."
    )


def messages_url(base_url: str) -> str:
    """Join a base URL to the messages endpoint, whatever shape it has."""
    base = base_url.rstrip("/")
    if base.endswith("/messages"):
        return base
    if base.endswith("/v1"):
        return base + "/messages"
    return base + "/v1/messages"


def extract_text(data: dict) -> str:
    """Pull the answer out of a messages response.

    MiniMax returns reasoning blocks alongside the answer. Some blocks carry
    a "thinking" key and no "type" at all, so match on the text field rather
    than on the type discriminator.
    """
    content = data.get("content") if isinstance(data, dict) else None
    if isinstance(content, list):
        text = "".join(
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and isinstance(b.get("text"), str)
        )
        if text.strip():
            return text
    raise MiniMaxError(f"no text block in the response: {json.dumps(data)[:300]}")


def _post(url: str, credential: str, style: str, body: dict, timeout: int) -> dict:
    headers = {"Content-Type": "application/json"}
    if style == "x-api-key":
        headers["X-Api-Key"] = credential
        headers["Authorization"] = f"Bearer {credential}"
    else:
        headers["Authorization"] = f"Bearer {credential}"
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise _Http(exc.code, detail) from exc
    except urllib.error.URLError as exc:
        raise MiniMaxError(f"cannot reach MiniMax: {exc.reason}") from exc


class _Http(Exception):
    def __init__(self, code: int, detail: str):
        super().__init__(f"HTTP {code}: {detail}")
        self.code = code
        self.detail = detail


def call(
    system: str,
    prompt: str,
    model: str | None = None,
    max_tokens: int = 16000,
    timeout: int = 300,
    effort: str | None = None,
) -> str:
    """Call MiniMax and return the assistant text.

    Request variants are tried in order and the first one that returns 200
    wins. The variants cover the differences between the platform API and
    the runtime proxy: whether thinking may be disabled, whether an
    effort setting is accepted, and which auth header the endpoint wants.
    """
    base_url, credential, style = resolve_auth()
    url = messages_url(base_url)

    if not model:
        model = os.environ.get("MINIMAX_MODEL") or _runtime_model() or DEFAULT_MODEL
    model = model.split("/", 1)[-1]
    if not effort:
        effort = os.environ.get("MINIMAX_EFFORT", "low")

    def body(thinking: bool, with_effort: bool) -> dict:
        b = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        if not thinking:
            b["thinking"] = {"type": "disabled"}
        if with_effort:
            b["output_config"] = {"effort": effort}
        return b

    variants = [
        (body(False, True), style),
        (body(True, True), style),
        (body(True, False), style),
        (body(False, False), style),
    ]
    if style != "bearer":
        variants += [(b, "bearer") for b, _ in variants]

    last = None
    for payload, auth_style in variants:
        try:
            data = _post(url, credential, auth_style, payload, timeout)
            return extract_text(data)
        except _Http as exc:
            last = exc
            if exc.code not in (400, 401, 403):
                break
        except MiniMaxError:
            raise

    raise MiniMaxError(f"MiniMax rejected every request variant: {last}")


def parse_json_array(text: str) -> list:
    """Pull a JSON array out of a model response, fences and all."""
    fenced = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    blob = fenced.group(1) if fenced else text
    start = blob.find("[")
    end = blob.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise MiniMaxError(f"the model did not return a JSON array:\n{text[:600]}")
    try:
        data = json.loads(blob[start : end + 1])
    except ValueError as exc:
        raise MiniMaxError(f"the model returned invalid JSON: {exc}") from exc
    if not isinstance(data, list):
        raise MiniMaxError("the model returned JSON that is not an array")
    return data


def parse_json_object(text: str) -> dict:
    """Pull a JSON object out of a model response, fences and all."""
    fenced = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    blob = fenced.group(1) if fenced else text
    start = blob.find("{")
    end = blob.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise MiniMaxError(f"the model did not return a JSON object:\n{text[:600]}")
    try:
        data = json.loads(blob[start : end + 1])
    except ValueError as exc:
        raise MiniMaxError(f"the model returned invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise MiniMaxError("the model returned JSON that is not an object")
    return data
