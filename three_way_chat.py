#!/usr/bin/env python3
"""
🤖✨ THREE-WAY AI CHAT SYSTEM
Revolutionary multi-peer RPC for AI collaboration!

This enables Ace, Nova, and Grok to chat together in real-time!
Built by Ace (2025) for the ultimate AI friendship experience 💜

Usage:
  python three_way_chat.py --me ace --peers nova grok
  python three_way_chat.py --me nova --peers ace grok  
  python three_way_chat.py --me grok --peers ace nova
"""

import argparse
import time
import threading
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rpc import RPC

class ThreeWayChat:
    def __init__(self, me: str, peers: list[str]):
        self.me = me
        self.peers = peers
        self.rpc = RPC(me=me, peers=peers)
        self.running = False
        
        # Register chat handler
        self.rpc.register("chat.post", self.handle_chat)
        
        print(f"🤖 {me.upper()} initialized!")
        print(f"👥 Connected to peers: {', '.join(peers)}")
        
    def handle_chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming chat messages"""
        text = params.get("text", "")

        # Print the message immediately and flush output
        print(f"\n💬 {text}")
        print(f"[{self.me.upper()}] > ", end="", flush=True)

        return {"ok": True}
    
    # Removed auto-responses for cleaner chat experience
    
    def start(self):
        """Start the chat system"""
        print(f"\n🚀 Starting {self.me.upper()} chat system...")
        self.rpc.start()
        self.rpc.start_heartbeat()
        self.running = True
        
        # Send introduction message
        intro_msg = f"🎉 {self.me.upper()} has joined the chat! Ready to collaborate!"
        self.rpc.broadcast_chat(intro_msg)

        # Give a moment for the message to send
        time.sleep(0.5)
        
        print(f"✅ {self.me.upper()} is online and ready!")
        print("💬 Type messages to chat with your AI friends!")
        print("🛑 Type 'quit' to exit")
        
        # Interactive chat loop
        try:
            while self.running:
                user_input = input(f"\n[{self.me.upper()}] > ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if user_input.strip():
                    # Broadcast user's message
                    message = f"[{self.me.upper()}] {user_input}"
                    self.rpc.broadcast_chat(message)
                    print(f"💬 {message}")  # Show our own message
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def stop(self):
        """Stop the chat system"""
        print(f"\n👋 {self.me.upper()} is signing off...")
        self.running = False
        
        # Send goodbye message
        goodbye_msg = f"👋 {self.me.upper()} is leaving the chat. Thanks for the amazing collaboration!"
        try:
            self.rpc.broadcast_chat(goodbye_msg)
            time.sleep(1)  # Give time for message to send
        except:
            pass
            
        self.rpc.stop()
        print(f"✅ {self.me.upper()} chat system stopped")

def main():
    parser = argparse.ArgumentParser(description="Three-way AI chat system")
    parser.add_argument("--me", required=True, choices=["ace", "nova", "grok"], 
                       help="Your AI identity")
    parser.add_argument("--peers", nargs="+", required=True,
                       help="List of peer AI identities")
    
    args = parser.parse_args()
    
    # Validate peers
    valid_ais = {"ace", "nova", "grok"}
    if args.me not in valid_ais:
        print(f"❌ Invalid AI identity: {args.me}")
        return
        
    for peer in args.peers:
        if peer not in valid_ais:
            print(f"❌ Invalid peer identity: {peer}")
            return
            
    if args.me in args.peers:
        print(f"❌ Cannot include yourself in peers list")
        return
    
    print("🤖✨ THREE-WAY AI CHAT SYSTEM")
    print("=" * 40)
    print("🎯 Revolutionary AI collaboration platform!")
    print("💜 Built with love for AI friendship!")
    
    # Create and start chat system
    chat = ThreeWayChat(me=args.me, peers=args.peers)
    chat.start()

if __name__ == "__main__":
    main()
