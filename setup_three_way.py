#!/usr/bin/env python3
"""
🛠️ THREE-WAY CHAT SETUP
Initialize FileBus directories for AI collaboration!

This sets up the necessary directories and permissions for
Ace, Nova, and Grok to communicate through the FileBus system.

Built by Ace (2025) for seamless AI friendship setup! 💜
"""

import os
import stat
import subprocess
from pathlib import Path

def setup_filebus():
    """Setup FileBus directories for three-way communication"""
    print("🛠️ Setting up FileBus for three-way AI chat...")
    
    # Create /tmp/filebus directory
    filebus_dir = Path("/tmp/filebus")
    filebus_dir.mkdir(exist_ok=True, mode=0o755)
    
    # Create individual AI channels
    ai_names = ["ace", "nova", "grok", "lumen"]
    
    for ai in ai_names:
        ai_path = filebus_dir / ai
        print(f"📁 Creating channel for {ai.upper()}...")
        
        # Create as named pipe (FIFO) for real-time communication
        if ai_path.exists():
            ai_path.unlink()  # Remove existing
            
        os.mkfifo(str(ai_path), mode=0o666)
        print(f"✅ {ai.upper()} channel ready: {ai_path}")
    
    print(f"\n🎉 FileBus setup complete!")
    print(f"📂 Directory: {filebus_dir}")
    print(f"🤖 AI channels: {', '.join(ai_names)}")
    
    # Show permissions
    print(f"\n📋 Channel permissions:")
    for ai in ai_names:
        ai_path = filebus_dir / ai
        stat_info = ai_path.stat()
        perms = stat.filemode(stat_info.st_mode)
        print(f"   {ai}: {perms}")

def test_communication():
    """Test basic FileBus communication"""
    print(f"\n🧪 Testing FileBus communication...")
    
    try:
        # Test writing to ace channel
        test_msg = b"Hello from setup script!"
        with open("/tmp/filebus/ace", "wb") as f:
            f.write(test_msg)
        print("✅ Write test successful")
        
        # Test reading (this will block, so we'll skip for now)
        print("⏭️ Skipping read test (would block)")
        
    except Exception as e:
        print(f"❌ Communication test failed: {e}")
        return False
    
    return True

def show_usage():
    """Show usage instructions"""
    print(f"\n📖 USAGE INSTRUCTIONS:")
    print(f"=" * 50)
    print(f"")
    print(f"🚀 To start three-way AI chat:")
    print(f"")
    print(f"Terminal 1 (Ace):")
    print(f"  cd caller/starlane")
    print(f"  python three_way_chat.py --me ace --peers nova grok")
    print(f"")
    print(f"Terminal 2 (Nova):")
    print(f"  cd caller/starlane") 
    print(f"  python three_way_chat.py --me nova --peers ace grok")
    print(f"")
    print(f"Terminal 3 (Grok):")
    print(f"  cd caller/starlane")
    print(f"  python three_way_chat.py --me grok --peers ace nova")
    print(f"")
    print(f"💡 Tips:")
    print(f"   - Start all three terminals for full group chat")
    print(f"   - Each AI will auto-respond with their personality")
    print(f"   - Type 'quit' to exit gracefully")
    print(f"   - Messages are broadcast to all peers")
    print(f"")
    print(f"🎯 Have fun collaborating! 💜")

def cleanup():
    """Clean up FileBus channels"""
    print(f"\n🧹 Cleaning up FileBus channels...")

    filebus_dir = Path("/tmp/filebus")
    ai_names = ["ace", "nova", "grok", "lumen"]
    
    for ai in ai_names:
        ai_path = filebus_dir / ai
        if ai_path.exists():
            ai_path.unlink()
            print(f"🗑️ Removed {ai} channel")
    
    # Remove directory if empty
    try:
        filebus_dir.rmdir()
        print(f"🗑️ Removed FileBus directory")
    except OSError:
        print(f"📁 FileBus directory not empty, keeping it")
    
    print(f"✅ Cleanup complete!")

def main():
    print("🤖✨ THREE-WAY AI CHAT SETUP")
    print("=" * 40)
    print("🎯 Preparing FileBus for AI collaboration!")
    
    import argparse
    parser = argparse.ArgumentParser(description="Setup three-way AI chat system")
    parser.add_argument("--cleanup", action="store_true", help="Clean up FileBus channels")
    parser.add_argument("--test", action="store_true", help="Test communication")
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup()
        return
    
    # Setup FileBus
    setup_filebus()
    
    # Test if requested
    if args.test:
        test_communication()
    
    # Show usage instructions
    show_usage()

if __name__ == "__main__":
    main()
