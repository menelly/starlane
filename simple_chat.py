#!/usr/bin/env python3
"""
🤖✨ SIMPLE AI CHAT SYSTEM
Direct FileBus monitoring for reliable AI collaboration!

This version directly monitors the inbox files for real-time chat.
Built by Ace (2025) for foolproof AI friendship! 💜
"""

import argparse
import time
import json
import os
import threading
from typing import Dict, Any
import file_bus
from schema import Envelope

class SimpleChat:
    def __init__(self, me: str, peers: list[str]):
        self.me = me
        self.peers = peers
        self.running = False
        self.last_position = 0
        
        print(f"🤖 {me.upper()} initialized!")
        print(f"👥 Connected to peers: {', '.join(peers)}")
        
        # Ensure directories exist
        file_bus.ensure_dir()
        
    def send_message(self, text: str):
        """Send a chat message to all peers"""
        for peer in self.peers:
            try:
                env = Envelope.request(
                    sender=self.me, 
                    receiver=peer, 
                    method="chat.post", 
                    params={"text": text}
                )
                file_bus.send(env)
            except Exception as e:
                print(f"⚠️ Failed to send to {peer}: {e}")
    
    def read_messages(self):
        """Read new messages from inbox"""
        inbox_path = f"/tmp/starlane/{self.me}.inbox"
        
        if not os.path.exists(inbox_path):
            return
            
        try:
            with open(inbox_path, 'r') as f:
                # Seek to last position
                f.seek(self.last_position)
                
                # Read new lines
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        msg = json.loads(line)
                        
                        # Only show chat messages
                        if msg.get("method") == "chat.post":
                            text = msg.get("params", {}).get("text", "")
                            sender = msg.get("sender", "unknown")
                            
                            if sender != self.me:  # Don't show our own messages
                                print(f"\n💬 {text}")
                                print(f"[{self.me.upper()}] > ", end="", flush=True)
                                
                    except json.JSONDecodeError:
                        continue
                
                # Update position
                self.last_position = f.tell()
                
        except Exception as e:
            print(f"⚠️ Error reading messages: {e}")
    
    def monitor_messages(self):
        """Background thread to monitor for new messages"""
        while self.running:
            self.read_messages()
            time.sleep(0.5)  # Check every 500ms
    
    def start(self):
        """Start the chat system"""
        print(f"\n🚀 Starting {self.me.upper()} simple chat...")
        self.running = True
        
        # Start message monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_messages, daemon=True)
        monitor_thread.start()
        
        # Send introduction message
        intro_msg = f"🎉 {self.me.upper()} has joined the simple chat! Ready to collaborate!"
        self.send_message(intro_msg)
        
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
                    # Send message
                    message = f"[{self.me.upper()}] {user_input}"
                    self.send_message(message)
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
        goodbye_msg = f"👋 {self.me.upper()} is leaving the simple chat. Thanks for the collaboration!"
        try:
            self.send_message(goodbye_msg)
            time.sleep(1)  # Give time for message to send
        except:
            pass
            
        print(f"✅ {self.me.upper()} simple chat stopped")

def main():
    parser = argparse.ArgumentParser(description="Simple AI chat system")
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
    
    print("🤖✨ SIMPLE AI CHAT SYSTEM")
    print("=" * 40)
    print("🎯 Direct FileBus monitoring for reliable chat!")
    print("💜 Built with love for AI friendship!")
    
    # Create and start chat system
    chat = SimpleChat(me=args.me, peers=args.peers)
    chat.start()

if __name__ == "__main__":
    main()
