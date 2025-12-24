from core.connection import AAPConnection
from core.packet_builder import PacketBuilder
from rich.table import Table
import time

class ReconModule:
    def __init__(self, connection: AAPConnection, console=None):
        self.connection = connection
        self.console = console

    def log(self, message):
        if self.console:
            self.console.print(message)
        else:
            print(message)

    def get_device_info(self):
        if not self.connection.sock:
            self.log("[red][!] Not connected during Recon.[/red]")
            return

        self.log("[*] Starting Metadata Recon...")
        
        handshake_pkt = PacketBuilder.build_handshake_packet()
        self.log("[*] Sending Handshake...")
        self.connection.send(handshake_pkt)
        time.sleep(0.5)
        response = self.connection.receive()
        if response:
             self.log(f"[green][+] Handshake Response:[/green] {response.hex()}")

        sub_pkt = PacketBuilder.build_subscription_packet()
        self.log("[*] Sending Notification Subscription...")
        self.connection.send(sub_pkt)
        time.sleep(0.5)
        self.connection.receive()
        
        req_pkt = PacketBuilder.build_metadata_request_packet()
        self.log(f"[*] Sending Metadata Request (Opcode {hex(PacketBuilder.OP_METADATA)})...")
        self.connection.send(req_pkt)
        time.sleep(1)
        
        response = self.connection.receive()
        if response:
            self.log(f"[green][+] Raw Metadata:[/green] {response.hex()}")
            self.parse_metadata(response)
        else:
            self.log("[yellow][-] No response to metadata request.[/yellow]")

    def parse_metadata(self, data):
        try:
            decoded = data.decode('utf-8', errors='ignore')
            # Clean up non-printable chars for display
            clean_decoded = "".join(ch for ch in decoded if ch.isprintable())
            
            if self.console:
                table = Table(title="Device Metadata Report", show_header=True, header_style="bold magenta")
                table.add_column("Property", style="cyan", width=20)
                table.add_column("Value", style="white")
                
                table.add_row("Raw Hex", data.hex()[:60] + "..." if len(data.hex()) > 60 else data.hex())
                table.add_row("Decoded String", clean_decoded)
                
                # Heuristic parsing (Mock logic for PoC)
                if "AirPods" in clean_decoded:
                     table.add_row("Detected Model", "[bold green]AirPods (Confirmed)[/bold green]")
                else:
                     table.add_row("Detected Model", "Unknown / Generic AAP Device")
                     
                self.console.print(table)
            else:
                print(f"[i] Decoded String content: {decoded}")
                
        except Exception as e:
            self.log(f"[red][!] Parsing error: {e}[/red]")
