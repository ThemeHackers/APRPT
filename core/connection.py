import socket
import time
import platform
import sys

class AAPConnection:
    def __init__(self, mac_address, console=None):
        self.mac_address = mac_address
        self.psm = 0x1001
        self.sock = None
        self.console = console

    def log(self, message, style=""):
        if self.console:
            self.console.print(message, style=style)
        else:
            print(message)

    def connect(self):
        if platform.system() != "Linux":
            self.log("[red][!] CRITICAL: This tool uses raw L2CAP sockets via BlueZ and is ONLY supported on Linux.[/red]")
            self.log(f"[!] Current detected OS: {platform.system()}")
            return False

        self.log(f"[*] Attempting to connect to [bold]{self.mac_address}[/bold] on PSM {hex(self.psm)}...")
        try:
            if not hasattr(socket, 'AF_BLUETOOTH') or not hasattr(socket, 'BTPROTO_L2CAP'):
                self.log("[red][!] Error: socket.AF_BLUETOOTH or BTPROTO_L2CAP not supported by this Python interpreter.[/red]")
                return False

            self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
            self.sock.connect((self.mac_address, self.psm))
            self.log(f"[green][+] Connected to {self.mac_address}[/green]")
            return True
        except Exception as e:
            self.log(f"[red][!] Connection failed: {e}[/red]")
            self.sock = None
            return False

    def send(self, data: bytes):
        if self.sock:
            try:
                self.sock.send(data)
                self.log(f"[blue][>][/blue] Sent {len(data)} bytes")
                return True
            except Exception as e:
                self.log(f"[red][!] Send failed: {e}[/red]")
        return False

    def receive(self, buffer_size=1024):
        if self.sock:
            try:
                data = self.sock.recv(buffer_size)
                self.log(f"[magenta][<][/magenta] Received {len(data)} bytes")
                return data
            except Exception as e:
                self.log(f"[red][!] Receive failed: {e}[/red]")
        return None

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            self.log("[*] Connection closed", style="dim")
