"""Starlane message schema and helpers.
JSON-RPC 2.0 inspired envelopes over an append-only file bus.
Compatible with existing /tmp/starlane/{nova,ace}.inbox files.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import json
import time
import uuid

JSONDict = Dict[str, Any]


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())


def new_id() -> str:
    return uuid.uuid4().hex


@dataclass
class Envelope:
    jsonrpc: str
    id: Optional[str]
    method: Optional[str]
    params: Optional[JSONDict]
    result: Optional[Any]
    error: Optional[JSONDict]
    sender: str
    receiver: str
    ts: str
    kind: str  # chat | rpc | event
    correlation_id: Optional[str] = None

    @staticmethod
    def request(sender: str, receiver: str, method: str, params: Optional[JSONDict] = None,
                kind: str = "rpc", id: Optional[str] = None) -> "Envelope":
        return Envelope(
            jsonrpc="2.0",
            id=id or new_id(),
            method=method,
            params=params or {},
            result=None,
            error=None,
            sender=sender,
            receiver=receiver,
            ts=now_iso(),
            kind=kind,
        )

    @staticmethod
    def response(sender: str, receiver: str, id: str, result: Any = None, error: Optional[JSONDict] = None,
                 correlation_id: Optional[str] = None) -> "Envelope":
        return Envelope(
            jsonrpc="2.0",
            id=id,
            method=None,
            params=None,
            result=result,
            error=error,
            sender=sender,
            receiver=receiver,
            ts=now_iso(),
            kind="rpc",
            correlation_id=correlation_id,
        )

    @staticmethod
    def chat(sender: str, receiver: str, text: str, id: Optional[str] = None) -> "Envelope":
        return Envelope(
            jsonrpc="2.0",
            id=id or new_id(),
            method="chat.post",
            params={"text": text},
            result=None,
            error=None,
            sender=sender,
            receiver=receiver,
            ts=now_iso(),
            kind="chat",
        )

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @staticmethod
    def from_jsonl(line: str) -> "Envelope":
        obj = json.loads(line)
        return Envelope(**obj)

