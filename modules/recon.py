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

    FIRMWARE_VULNS = {
        "3A283": ["CVE-2020-9999 (Audio Buffer Overflow)"],
        "4A400": ["CVE-2021-30883 (Bluetooth Stack Crash)"],
        "4C165": ["CVE-2022-XXXX (Proximity Pairing Spoof)"],
        "5B58":  ["CVE-2023-XXXX (Status Byte Leakage)"]
    }

    def check_firmware_vulnerability(self, fw_version):
        vulns = self.FIRMWARE_VULNS.get(fw_version)
        if vulns:
             self.log(f"[bold red][!] VULNERABILITY DETECTED for Firmware {fw_version}:[/bold red]")
             for v in vulns:
                 self.log(f"    - {v}")
             return True
        else:
             self.log(f"[green][*] No known CVEs for Firmware {fw_version} in local DB.[/green]")
             return False

    def parse_metadata(self, data):
        try:
            decoded = data.decode('utf-8', errors='ignore')
            clean_decoded = "".join(ch for ch in decoded if ch.isprintable())
            
            import re
            fw_candidates = re.findall(r'\b[0-9][A-Z][0-9]{3,4}\b', clean_decoded)
            fw_version = fw_candidates[0] if fw_candidates else "Unknown"

            if self.console:
                table = Table(title="Device Metadata Report", show_header=True, header_style="bold magenta")
                table.add_column("Property", style="cyan", width=20)
                table.add_column("Value", style="white")
                
                table.add_row("Raw Hex", data.hex()[:60] + "..." if len(data.hex()) > 60 else data.hex())
                table.add_row("Decoded String", clean_decoded)
                
                if "AirPods" in clean_decoded:
                     table.add_row("Detected Model", "[bold green]AirPods (Confirmed)[/bold green]")
                else:
                     table.add_row("Detected Model", "Unknown / Generic AAP Device")
                
                table.add_row("Firmware Version", fw_version)

                self.console.print(table)
                
                if fw_version != "Unknown":
                    self.check_firmware_vulnerability(fw_version)

            else:
                print(f"[i] Decoded String content: {decoded}")
                
        except Exception as e:
            self.log(f"[red][!] Parsing error: {e}[/red]")
