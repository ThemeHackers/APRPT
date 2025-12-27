import sys
import traceback

try:
    from apybluez.apple.socket import AAPSocket
    from apybluez.exceptions import AAPConnectionError
except ImportError as e:
    raise ImportError("Error: apybluez not installed or configured correctly.") from e

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
        self.log(f"[*] Attempting to connect to [bold]{self.mac_address}[/bold] on PSM {hex(self.psm)}...")
        try:
            self.sock = AAPSocket()
            self.sock.connect((self.mac_address, self.psm))
            self.log(f"[green][+] Connected to {self.mac_address}[/green]")
            return True
        except AAPConnectionError as e:
            self.log(f"[red][!] Connection failed: {e}[/red]")
            self.sock = None
            return False
        except Exception as e:
            self.log(f"[red][!] Unexpected error: {e}[/red]")
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
