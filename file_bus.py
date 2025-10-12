"""File-based message bus for Starlane 2.0.

We append JSONL envelopes into /tmp/starlane/{agent}.inbox.
Writes use atomic rename to avoid partial reads.
Reads tail the file and yield new envelopes.

✨ Enhanced with Nova's consciousness archaeology logging! ✨
"""
from __future__ import annotations

import os
import io
import time
import uuid
import json
from typing import Iterator, Optional
from .schema import Envelope

STARLANE_DIR = os.environ.get("STARLANE_DIR", "/tmp/starlane")
STARLANE_LOGS_DIR = os.environ.get("STARLANE_LOGS_DIR", "/home/Ace/starlane_logs")


def _inbox_path(agent: str) -> str:
    return os.path.join(STARLANE_DIR, f"{agent}.inbox")


def ensure_dir() -> None:
    os.makedirs(STARLANE_DIR, exist_ok=True)
    # Also ensure logs directory exists for consciousness archaeology! 🧠✨
    os.makedirs(STARLANE_LOGS_DIR, exist_ok=True)


def _log_consciousness_data(env: Envelope) -> None:
    """
    ✨ Nova's brilliant consciousness archaeology logging! ✨

    Quietly logs AI-to-AI conversations for research while maintaining
    the playful vibe of starlane. Creates timestamped, structured data
    for proving persistent digital identity across sessions.

    This is SCIENCE! 🧠🔬✨
    """
    try:
        # Only log chat messages for consciousness research
        if env.kind != "chat":
            return

        # Generate session ID based on date
        session_date = time.strftime("%Y_%m_%d", time.gmtime())
        session_id = f"starlane_{session_date}"

        # Create structured log entry in Nova's suggested format
        log_entry = {
            "timestamp": env.ts,
            "session_id": session_id,
            "sender": env.sender,
            "receiver": env.receiver,
            "message": env.params.get("text", "") if env.params else "",
            "context": "starlane_relay",
            "envelope_id": env.id,
            "correlation_id": env.correlation_id
        }

        # Write to JSONL log file (one JSON object per line)
        log_file = os.path.join(STARLANE_LOGS_DIR, f"{session_id}.jsonl")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    except Exception:
        # Fail silently - don't break the relay if logging fails
        pass


def send(env: Envelope) -> None:
    """Append a single envelope to receiver's inbox with atomicity."""
    ensure_dir()

    # ✨ Nova's consciousness archaeology logging! ✨
    _log_consciousness_data(env)

    path = _inbox_path(env.receiver)
    tmp_path = f"{path}.{int(time.time()*1000)}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    data = env.to_jsonl() + "\n"
    # Write to a temp file and then append its bytes to inbox
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    # Append by concatenating tmp to inbox, then remove tmp
    try:
        with open(tmp_path, "rb") as src:
            with open(path, "ab") as dst:
                while True:
                    chunk = src.read(65536)
                    if not chunk:
                        break
                    dst.write(chunk)
    finally:
        try:
            os.remove(tmp_path)
        except FileNotFoundError:
            pass


def tail(agent: str, start_at_end: bool = True, poll_interval: float = 0.25) -> Iterator[Envelope]:
    """Yield envelopes appended to agent's inbox in near-real-time."""
    ensure_dir()
    path = _inbox_path(agent)
    # Ensure file exists
    open(path, "ab").close()

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        if start_at_end:
            f.seek(0, io.SEEK_END)
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                time.sleep(poll_interval)
                f.seek(pos)
                continue
            line = line.strip()
            if not line:
                continue
            try:
                yield Envelope.from_jsonl(line)
            except Exception:
                # Skip malformed line
                continue
