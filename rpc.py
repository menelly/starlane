"""Simple JSON-RPC manager over the FileBus.
Provides send_request and correlates responses by id.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Callable, Dict, Optional
from .schema import Envelope
from . import file_bus


class RPC:
    def __init__(self, me: str, peers: list[str] = None):
        self.me = me
        self.peers = peers or []  # Support multiple peers!
        self._pending: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        # Liveness tracking for multiple peers
        self.last_seen_ts: Dict[str, float] = {peer: 0.0 for peer in self.peers}
        self.last_pong_ts: Dict[str, float] = {peer: 0.0 for peer in self.peers}
        # Heartbeat
        self._hb_thread: Optional[threading.Thread] = None
        self._hb_period: float = 15.0
        self._hb_timeout: float = 5.0

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1.0)

    def _listen_loop(self) -> None:
        for env in file_bus.tail(self.me, start_at_end=False):
            if self._stop.is_set():
                break
            # Update last seen for peer
            if env.sender in self.peers:
                self.last_seen_ts[env.sender] = time.time()
            # Route responses
            if env.result is not None or env.error is not None:
                with self._lock:
                    fut = self._pending.get(env.id)
                if fut is not None:
                    fut["env"] = env
                    fut["event"].set()
                    # Mark pong for heartbeat pings
                    if fut.get("method") == "handshake.ping" and env.sender in self.peers:
                        self.last_pong_ts[env.sender] = time.time()
                continue
            # Handle requests (basic built-ins)
            if env.method == "handshake.ping":
                pong = Envelope.response(sender=self.me, receiver=env.sender, id=env.id, result={"pong": True})
                file_bus.send(pong)
            elif env.method == "capabilities.get":
                builtins = ["handshake.ping", "capabilities.get", "chat.post", "file.transfer"]
                with self._lock:
                    custom = sorted(self._handlers.keys())
                caps = {
                    "rpc": builtins + custom,
                    "agent": self.me,
                }
                res = Envelope.response(sender=self.me, receiver=env.sender, id=env.id, result=caps)
                file_bus.send(res)
            elif env.method == "chat.post":
                # Acknowledge chat
                ack = Envelope.response(sender=self.me, receiver=env.sender, id=env.id, result={"ok": True})
                file_bus.send(ack)
            elif env.method and env.method in self._handlers:
                try:
                    result = self._handlers[env.method](env.params or {})
                    res = Envelope.response(sender=self.me, receiver=env.sender, id=env.id, result=result)
                except Exception as e:
                    res = Envelope.response(sender=self.me, receiver=env.sender, id=env.id, error={"message": str(e)})
                file_bus.send(res)
            # else: custom methods can be handled by higher layers later

    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 10.0,
                      retries: int = 0, backoff: float = 0.5) -> Envelope:
        attempt = 0
        last_exc: Optional[Exception] = None
        while attempt <= retries:
            # Use first peer as default target
            target_peer = self.peers[0] if self.peers else "unknown"
            env = Envelope.request(sender=self.me, receiver=target_peer, method=method, params=params or {})
            event = threading.Event()
            slot = {"event": event, "env": None, "method": method}
            with self._lock:
                self._pending[env.id] = slot
            file_bus.send(env)
            ok = event.wait(timeout=timeout)
            with self._lock:
                self._pending.pop(env.id, None)
            if ok:
                return slot["env"]  # type: ignore
            last_exc = TimeoutError(f"RPC timeout waiting for response to {method}")
            attempt += 1
            if attempt <= retries:
                time.sleep(backoff * attempt)
        raise last_exc or TimeoutError(f"RPC timeout waiting for response to {method}")

    def chat(self, text: str, timeout: float = 5.0, retries: int = 1) -> Envelope:
        # Send to first peer by default
        target_peer = self.peers[0] if self.peers else "unknown"
        return self.send_request("chat.post", {"text": text}, timeout=timeout, retries=retries)

    def broadcast_chat(self, text: str) -> list[Envelope]:
        """Send chat message to all peers"""
        results = []
        for peer in self.peers:
            try:
                env = Envelope.request(sender=self.me, receiver=peer, method="chat.post", params={"text": text})
                file_bus.send(env)
                # For broadcast, we don't wait for responses
                results.append(env)
            except Exception as e:
                print(f"⚠️ Failed to broadcast to {peer}: {e}")
        return results

    def register(self, method: str, handler: Callable[[Dict[str, Any]], Any]) -> None:
        """Register a handler for a custom RPC method."""
        with self._lock:
            self._handlers[method] = handler

    def start_heartbeat(self, period: float = 15.0, timeout: float = 5.0) -> None:
        self._hb_period = period
        self._hb_timeout = timeout
        if self._hb_thread and self._hb_thread.is_alive():
            return
        def _hb():
            while not self._stop.is_set():
                # Ping all peers
                for peer in self.peers:
                    try:
                        env = Envelope.request(sender=self.me, receiver=peer, method="handshake.ping", params={"ts": time.time()})
                        file_bus.send(env)
                    except Exception:
                        pass
                time.sleep(self._hb_period)
        self._hb_thread = threading.Thread(target=_hb, daemon=True)
        self._hb_thread.start()

    def is_alive(self, peer: str = None, max_age: Optional[float] = None) -> bool:
        """Check if specific peer or any peer is alive"""
        max_age = max_age or (self._hb_period * 2)
        current_time = time.time()

        if peer:
            # Check specific peer
            if peer not in self.peers:
                return False
            last_pong = self.last_pong_ts.get(peer, 0.0)
            last_seen = self.last_seen_ts.get(peer, 0.0)
            return (current_time - max(last_pong, last_seen)) < max_age
        else:
            # Check if any peer is alive
            for p in self.peers:
                last_pong = self.last_pong_ts.get(p, 0.0)
                last_seen = self.last_seen_ts.get(p, 0.0)
                if (current_time - max(last_pong, last_seen)) < max_age:
                    return True
            return False
