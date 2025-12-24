import struct
import sys
import socket
import time
from rich.console import Console

class ControlModule:
    def __init__(self, console=None, dev_id=0, target=None):
        self.console = console if console else Console()
        self.dev_id = dev_id
        self.target = target
        self.sock = None
        
    def log(self, msg):
        self.console.print(msg)

    def connect(self):
        if not self.target:
            self.log("[red][!] Target MAC address required for Control Mode.[/red]")
            return False
            
        self.log(f"[bold blue][*] Connecting to {self.target} via L2CAP (PSM 0x1001)...[/bold blue]")
        
        try:
            self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
            self.sock.connect((self.target, 0x1001))
            self.log("[green][+] Connected![/green]")
            return True
        except Exception as e:
            self.log(f"[red][!] Connection failed: {e}[/red]")
            return False

    def send_handshake(self):
        handshake = bytes.fromhex("00 00 04 00 01 00 02 00 00 00 00 00 00 00 00 00")
        try:
            self.sock.send(handshake)
            self.log("[green][*] Handshake sent.[/green]")
        except Exception as e:
            self.log(f"[red][!] Handshake failed: {e}[/red]")

    def set_noise_control(self, mode):
        header = b'\x04\x00\x04\x00'
        opcode = b'\x09\x00' 
        subcmd = b'\x0D' 
        mode_byte = bytes([mode])
        padding = b'\x00\x00\x00'
        
        packet = header + opcode + subcmd + mode_byte + padding
        
        try:
            self.sock.send(packet)
            modes = {1: "OFF", 2: "ANC", 3: "TRANSPARENCY"}
            self.log(f"[bold yellow][*] Sent Noise Control Command: {modes.get(mode, 'UNKNOWN')}[/bold yellow]")
        except Exception as e:
            self.log(f"[red][!] Failed to send command: {e}[/red]")

    def start_control(self):
        if not self.connect():
            return
            
        self.send_handshake()
        time.sleep(1)
        
        self.log("\n[bold]Choose Action:[/bold]")
        self.log("1. Force Transparency (Hear Environment)")
        self.log("2. Force ANC (Silence)")
        self.log("3. Force Off (Normal)")
        
        try:
            while True:
                choice = input("\naprpt-control > ")
                if choice == "1":
                    self.set_noise_control(0x03)
                elif choice == "2":
                    self.set_noise_control(0x02)
                elif choice == "3":
                    self.set_noise_control(0x01)
                elif choice == "exit":
                    break
        except KeyboardInterrupt:
            pass
            
        self.log("[*] Closing connection...")
        self.sock.close()
