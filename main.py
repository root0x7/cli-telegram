#!/usr/bin/env python3

import asyncio
import os
import sys
from datetime import datetime
from typing import Optional, List
from telethon import TelegramClient
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
import threading
import queue
from dotenv import load_dotenv

load_dotenv()

class SimpleTelegramTUI:
    def __init__(self):
        self.console = Console()
        self.api_id = os.getenv('TG_API_ID', 'YOUR_API_ID')
        self.api_hash = os.getenv('TG_API_HASH', 'YOUR_API_HASH')
        self.phone = os.getenv('TG_PHONE')
        self.session_name = 'telegram_simple_tui'
        self.client = None
        self.chats = []
        self.current_chat = None
        self.current_chat_name = "No chat selected"
        self.messages = []
        self.running = True
        self.selected_chat_index = 0
        self.message_queue = queue.Queue()
        
    def check_credentials(self):
        if self.api_id == 'YOUR_API_ID' or self.api_hash == 'YOUR_API_HASH':
            self.console.print("❌ [red]Please set environment variables:[/red]")
            self.console.print("export TG_API_ID='your_api_id'")
            self.console.print("export TG_API_HASH='your_api_hash'")
            self.console.print("export TG_PHONE='your_phone_number'")
            self.console.print("\n📚 Get API credentials from: https://my.telegram.org")
            return False
        return True
    
    async def initialize_client(self):
        try:
            if not self.phone:
                self.phone = Prompt.ask("📱 Enter your phone number (with country code)")
            self.console.print("🔄 Connecting to Telegram...")
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.start(phone=self.phone)
            me = await self.client.get_me()
            self.console.print(f"✅ Logged in as: {me.first_name} {me.last_name or ''}")
            return True
        except Exception as e:
            self.console.print(f"❌ Connection failed: {str(e)}")
            return False
    
    async def load_chats(self):
        try:
            self.console.print("📋 Loading chats...")
            self.chats = []
            async for dialog in self.client.iter_dialogs(limit=30):
                chat_info = {
                    'entity': dialog.entity,
                    'name': getattr(dialog.entity, 'title', None) or getattr(dialog.entity, 'first_name', 'Unknown'),
                    'id': dialog.entity.id,
                    'unread': dialog.unread_count,
                    'type': '👤' if hasattr(dialog.entity, 'first_name') else '👥'
                }
                self.chats.append(chat_info)
            self.console.print(f"✅ Loaded {len(self.chats)} chats")
            return True
        except Exception as e:
            self.console.print(f"❌ Failed to load chats: {str(e)}")
            return False
    
    async def load_messages(self, chat_entity, limit=20):
        try:
            self.messages = []
            async for message in self.client.iter_messages(chat_entity, limit=limit):
                if message.text:
                    msg_info = {
                        'time': message.date.strftime("%H:%M"),
                        'sender': "You" if message.out else getattr(message.sender, 'first_name', 'Unknown'),
                        'text': message.text[:100] + ('...' if len(message.text) > 100 else ''),
                        'is_out': message.out,
                        'full_text': message.text
                    }
                    self.messages.insert(0, msg_info)
            return True
        except Exception as e:
            self.console.print(f"❌ Failed to load messages: {str(e)}")
            return False
    
    def create_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=5)
        )
        layout["body"].split_row(
            Layout(name="chat_list", ratio=1),
            Layout(name="messages", ratio=2)
        )
        return layout
    
    def render_header(self):
        return Panel(
            Text("📱 Telegram TUI Client", style="bold blue", justify="center"),
            style="bold blue"
        )
    
    def render_chat_list(self):
        table = Table(title="💬 Chats", show_header=False, box=None)
        table.add_column("Chat", style="cyan", no_wrap=True)
        for i, chat in enumerate(self.chats):
            style = "bold green" if i == self.selected_chat_index else "white"
            marker = "► " if i == self.selected_chat_index else "  "
            unread_info = f" ({chat['unread']})" if chat['unread'] > 0 else ""
            table.add_row(
                f"{marker}{chat['type']} {chat['name']}{unread_info}",
                style=style
            )
        return Panel(table, title="Chats", border_style="blue")
    
    def render_messages(self):
        if not self.messages:
            content = Text("Select a chat to view messages", style="dim", justify="center")
            return Panel(content, title=self.current_chat_name, border_style="green")
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Time", style="dim", width=8)
        table.add_column("Sender", style="bold", width=15)
        table.add_column("Message", style="white")
        for msg in self.messages[-15:]:
            sender_style = "green" if msg['is_out'] else "blue"
            table.add_row(
                msg['time'],
                Text(msg['sender'], style=sender_style),
                msg['text']
            )
        return Panel(table, title=f"💬 {self.current_chat_name}", border_style="green")
    
    def render_footer(self):
        help_text = Text()
        help_text.append("Commands: ", style="bold")
        help_text.append("↑↓", style="cyan")
        help_text.append(" Navigate | ", style="white")
        help_text.append("Enter", style="cyan") 
        help_text.append(" Select | ", style="white")
        help_text.append("s", style="cyan")
        help_text.append(" Send | ", style="white")
        help_text.append("r", style="cyan")
        help_text.append(" Refresh | ", style="white")
        help_text.append("q", style="cyan")
        help_text.append(" Quit", style="white")
        return Panel(help_text, title="Help", border_style="yellow")
    
    async def send_message(self, text):
        if not self.current_chat:
            self.console.print("❌ No chat selected")
            return False
        try:
            await self.client.send_message(self.current_chat, text)
            new_msg = {
                'time': datetime.now().strftime("%H:%M"),
                'sender': "You",
                'text': text[:100] + ('...' if len(text) > 100 else ''),
                'is_out': True,
                'full_text': text
            }
            self.messages.append(new_msg)
            return True
        except Exception as e:
            self.console.print(f"❌ Failed to send message: {str(e)}")
            return False
    
    def get_input(self):
        import select
        import tty
        import termios
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            if select.select([sys.stdin], [], [], 0.1)[0]:
                return sys.stdin.read(1)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        return None
    
    async def run_simple(self):
        if not self.check_credentials():
            return
        if not await self.initialize_client():
            return
        if not await self.load_chats():
            return
        while self.running:
            self.console.clear()
            self.console.print(self.render_header())
            self.console.print(self.render_chat_list())
            if self.current_chat:
                self.console.print(self.render_messages())
            self.console.print(self.render_footer())
            try:
                command = Prompt.ask("\nEnter command", choices=["up", "down", "select", "send", "refresh", "quit"], default="quit")
                if command == "quit":
                    break
                elif command == "up" and self.selected_chat_index > 0:
                    self.selected_chat_index -= 1
                elif command == "down" and self.selected_chat_index < len(self.chats) - 1:
                    self.selected_chat_index += 1
                elif command == "select":
                    if self.chats:
                        selected_chat = self.chats[self.selected_chat_index]
                        self.current_chat = selected_chat['entity']
                        self.current_chat_name = selected_chat['name']
                        await self.load_messages(self.current_chat)
                elif command == "send":
                    if self.current_chat:
                        message = Prompt.ask("Enter message")
                        if message:
                            await self.send_message(message)
                elif command == "refresh":
                    await self.load_chats()
                    if self.current_chat:
                        await self.load_messages(self.current_chat)
            except KeyboardInterrupt:
                break
        self.console.print("👋 Goodbye!")
        if self.client:
            await self.client.disconnect()
    
    async def run_interactive(self):
        if not self.check_credentials():
            return
        if not await self.initialize_client():
            return
        if not await self.load_chats():
            return
        layout = self.create_layout()
        with Live(layout, console=self.console, screen=True, auto_refresh=False) as live:
            while self.running:
                layout["header"].update(self.render_header())
                layout["chat_list"].update(self.render_chat_list())
                layout["messages"].update(self.render_messages())
                layout["footer"].update(self.render_footer())
                live.refresh()
                key = self.get_input()
                if key:
                    if key.lower() == 'q':
                        break
                    elif key == '\x1b':
                        pass
                    elif key.lower() == 'r':
                        await self.load_chats()
                        if self.current_chat:
                            await self.load_messages(self.current_chat)
                await asyncio.sleep(0.1)
        if self.client:
            await self.client.disconnect()

def main():
    tui = SimpleTelegramTUI()
    try:
        asyncio.run(tui.run_simple())
    except Exception as e:
        print(f"Error: {e}")
        print("\nTry installing required packages:")
        print("pip install telethon rich")

if __name__ == '__main__':
    main()
