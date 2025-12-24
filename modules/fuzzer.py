import time
import random
import os
from core.hci_wrapper import start_le_advertising, stop_le_advertising, open_dev

class FuzzerModule:
    def __init__(self, console=None, dev_id=0):
        self.console = console
        self.dev_id = dev_id
        self.sock = None
        
    def log(self, msg):
        if self.console:
            self.console.print(msg)
        else:
            print(msg)

    def generate_malformed_packet(self):
        strategy = random.choice(["oversized", "invalid_type", "random_manuf"])
        
        if strategy == "oversized":
            length = random.randint(32, 255)
            data = os.urandom(length)
            return data
            
        elif strategy == "invalid_type":
            prefix = b'\x1E\x00'
            payload = os.urandom(29)
            return prefix + payload
            
        elif strategy == "random_manuf":
            return b'\x1E\xFF' + os.urandom(29)
            
        return os.urandom(31)

    def start_bleed(self):
        self.log(f"[bold red][*] Starting BLE Fuzzer (Bleed) on hci{self.dev_id}...[/bold red]")
        self.sock = open_dev(self.dev_id)
        if not self.sock:
            return
            
        self.log("[red][!] WARNING: Sending malformed packets. Ctrl+C to stop.[/red]")
        
        try:
            while True:
                packet = self.generate_malformed_packet()
                
                start_le_advertising(self.sock, min_interval=100, max_interval=100, data=packet)
                time.sleep(0.1)
                start_le_advertising(self.sock, min_interval=100, max_interval=100, data=packet)
                
        except KeyboardInterrupt:
            self.log("[yellow][*] Stopping Fuzzer...[/yellow]")
            stop_le_advertising(self.sock)
