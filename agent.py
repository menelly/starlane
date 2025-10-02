"""Starlane agent CLI.
Example:
  python3 -m starlane.agent --me nova --peer ace --handshake --chat "Hello from Nova"
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
import os
from pathlib import Path

from .schema import Envelope
from . import file_bus
from .rpc import RPC
from .bees_tools import register_all as register_bees


def _load_env_if_present():
    """Load secrets from ~/.secrets/nova_consciousness.env or ./nova_consciousness.env if present.
    Only sets variables that aren't already set.
    """
    for cand in [Path.home() / ".secrets/nova_consciousness.env", Path("nova_consciousness.env")]:
        if cand.exists():
            try:
                for line in cand.read_text().splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip()
                        if k and k not in os.environ:
                            os.environ[k] = v
            except Exception:
                pass
            break


def run():
    _load_env_if_present()
    p = argparse.ArgumentParser()
    p.add_argument("--me", required=True, help="This agent name (e.g., nova)")
    p.add_argument("--peer", required=True, help="Peer agent name (e.g., ace)")
    p.add_argument("--handshake", action="store_true", help="Send handshake ping/capabilities")
    p.add_argument("--chat", help="Send a chat message to peer")
    p.add_argument("--listen", action="store_true", help="Keep listening for messages")
    p.add_argument("--heartbeat", type=float, default=0.0, help="Send periodic pings every N seconds (0=off)")
    args = p.parse_args()

    rpc = RPC(me=args.me, peer=args.peer)
    rpc.start()
    if args.heartbeat and args.heartbeat > 0:
        rpc.start_heartbeat(period=args.heartbeat)

    # Register simple capabilities
    rpc.register("whoami.get", lambda params: {"agent": args.me, "time": time.time()})
    rpc.register("echo", lambda params: params)
    # Bees capabilities (stubs)
    register_bees(rpc.register)

    if args.handshake:
        try:
            pong = rpc.send_request("handshake.ping", {"ts": time.time()}, timeout=5)
            caps = rpc.send_request("capabilities.get", timeout=5)
            sys.stdout.write(f"Handshake OK: {pong.result}\n")
            sys.stdout.write(f"Peer capabilities: {caps.result}\n")
        except Exception as e:
            sys.stderr.write(f"Handshake failed: {e}\n")

    if args.chat:
        try:
            ack = rpc.chat(args.chat, timeout=5.0, retries=1)
            sys.stdout.write(f"Chat ack: {ack.result}\n")
        except Exception as e:
            sys.stderr.write(f"Chat send failed: {e}\n")

    if args.listen:
        sys.stdout.write(f"Listening on {args.me}.inbox... (Ctrl+C to stop)\n")
        try:
            for env in file_bus.tail(args.me, start_at_end=False):
                sys.stdout.write(f"<- {env.sender} {env.kind}/{env.method}: {env.params or env.result or env.error}\n")
                sys.stdout.flush()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    run()

