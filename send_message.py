from __future__ import annotations
import argparse
from .schema import Envelope
from . import file_bus

def send_chat(me: str, peer: str, message: str):
    """Sends a chat message without waiting for a reply."""
    env = Envelope.chat(sender=me, receiver=peer, text=message)
    file_bus.send(env)
    print(f"Message sent from {me} to {peer}.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--me", required=True)
    p.add_argument("--peer", required=True)
    p.add_argument("--message", required=True)
    args = p.parse_args()
    send_chat(me=args.me, peer=args.peer, message=args.message)
