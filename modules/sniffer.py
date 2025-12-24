import struct
import select
import sys
import bluetooth._bluetooth as bluez
from rich.table import Table
from rich.live import Live
from core.hci_wrapper import open_dev, enable_le_scan

class SnifferModule:
    def __init__(self, console=None, dev_id=0):
        self.console = console
        self.dev_id = dev_id
        self.sock = None
        self.devices = {}

    def log(self, msg):
        if self.console:
            self.console.print(msg)
        else:
            print(msg)

    def decode_proximity_packet(self, data):









        
        if len(data) < 20: return {}
        
        info = {"raw": data.hex()}
        

        pairing_byte = data[1]
        is_pairing = (pairing_byte & 0x01) == 0x01
        





        model_bytes = data[2:4]
        model_hex = model_bytes.hex()
        
        models = {
            "0220": "AirPods",
            "0e20": "AirPods Pro",
            "0a20": "AirPods Max",
            "0f20": "AirPods Gen 2",
            "1320": "AirPods Gen 3",
            "1420": "AirPods Pro 2",
        }
        
        model_name = models.get(model_hex, f"Unknown ({model_hex})")
        if is_pairing:
            model_name = f"[bold blink red] !!! SPOOF DETECTED !!! [/bold blink red] {model_name}"
        
        info["model"] = model_name
        
        status_byte = data[4]
        info["status_raw"] = f"{status_byte:02x}"
        
        bat_byte = data[5]
        bat_left = (bat_byte >> 4) & 0x0F
        bat_right = bat_byte & 0x0F
        
        def dec_bat(val):
            if val == 0xF: return "?"
            if val == 0xA: return "100%"
            return f"{val * 10}%"
            
        info["bat_L"] = dec_bat(bat_left)
        info["bat_R"] = dec_bat(bat_right)
        
        case_byte = data[6]
        bat_case = (case_byte >> 4) & 0x0F
        
        info["bat_C"] = dec_bat(bat_case)
        
        lid_byte = data[7]
        info["lid_open"] = (lid_byte & 0x01) != 0


        lid_counter = (lid_byte >> 1) & 0x07
        if lid_counter == 0 or lid_counter == 1:

             pass
        
        return info

    def start_sniff(self):
        self.log(f"[bold blue][*] Starting Passive Sniffer on hci{self.dev_id}...[/bold blue]")
        self.sock = open_dev(self.dev_id)
        if not self.sock:
            return

        enable_le_scan(self.sock, enabled=True)
        

        pass
        
        table = Table(title="Apple Devices Detected", show_lines=True)
        table.add_column("MAC", style="cyan")
        table.add_column("Model")
        table.add_column("Battery (L/R/C)")
        table.add_column("Lid Open")
        table.add_column("RSSI", style="green")
        table.add_column("Last Seen", style="dim")
        
        import datetime

        try:
            with Live(table, console=self.console, refresh_per_second=4, screen=False) as live:
                while True:
                    readable, _, _ = select.select([self.sock], [], [], 1)
                    if self.sock in readable:
                        pkt = self.sock.recv(255)
                        ptype, event, plen = struct.unpack("BBB", pkt[:3])
                        
                        if event == 0x3E:
                            subevent, _ = struct.unpack("BB", pkt[3:5])
                            if subevent == 0x02:
                                num_reports = pkt[5]
                                offset = 6
                                for i in range(num_reports):


                                    mac_bytes = pkt[offset+2 : offset+8]
                                    mac_str = ':'.join('%02x' % b for b in reversed(mac_bytes))
                                    data_len = pkt[offset+8]
                                    data = pkt[offset+9 : offset+9+data_len]
                                    rssi = struct.unpack("b", pkt[offset+9+data_len:offset+9+data_len+1])[0]
                                    
                                    offset += 9 + data_len + 1
                                    




                                    
                                    if len(data) > 4 and data[1] == 0xFF and data[2] == 0x4C and data[3] == 0x00:
                                        subtype = data[4]
                                        payload = data[5:]
                                        
                                        decoded = {}
                                        if subtype == 0x07:
                                            decoded = self.decode_proximity_packet(payload)
                                        elif subtype == 0x10:
                                         
                                            decoded = self.decode_proximity_packet(payload)
                                            if "model" in decoded:
                                                decoded["model"] = f"Nearby Info (0x10) - {decoded['model']}"
                                            else:
                                                 decoded["model"] = "Nearby Info (0x10)"
                                        else:
                                            decoded = {"model": f"Other Apple (0x{subtype:02x})"}
                                            

                                        now = datetime.datetime.now().strftime("%H:%M:%S")
                                        
                                        bat_str = f"{decoded.get('bat_L','?')}/{decoded.get('bat_R','?')}/{decoded.get('bat_C','?')}"
                                        model_str = decoded.get('model', 'Unknown')
                                        lid_str = "Yes" if decoded.get('lid_open') else "No"
                                        
                                        self.devices[mac_str] = {
                                            "model": model_str,
                                            "bat": bat_str,
                                            "lid": lid_str,
                                            "rssi": str(rssi),
                                            "seen": now
                                        }
                                        









                                        
                                        new_table = Table(title="Apple Devices Detected (Passive Scan)", show_lines=True)
                                        new_table.add_column("MAC", style="cyan")
                                        new_table.add_column("Model")
                                        new_table.add_column("Battery (L/R/C)")
                                        new_table.add_column("Lid Open")
                                        new_table.add_column("RSSI", style="green")
                                        new_table.add_column("Last Seen", style="dim")
                                        
                                        for m, d in self.devices.items():
                                            new_table.add_row(m, d['model'], d['bat'], d['lid'], d['rssi'], d['seen'])
                                        
                                        live.update(new_table)

        except KeyboardInterrupt:
            self.log("\n[yellow][*] Stopping Sniffer...[/yellow]")
            enable_le_scan(self.sock, enabled=False)
