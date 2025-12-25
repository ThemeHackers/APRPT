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

    def start_sniff(self, target_mac=None, output_file=None, callback=None):
        target_str = f" [bold red]TARGETING {target_mac}[/bold red]" if target_mac else ""
        self.log(f"[bold blue][*] Starting Passive Sniffer on hci{self.dev_id}...{target_str}[/bold blue]")
        
        self.sock = open_dev(self.dev_id)
        if not self.sock:
            return

        try:
            flt = bluez.hci_filter_new()
            bluez.hci_filter_all_events(flt)
            bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
            self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
            self.log("[green][*] HCI Filter set to allow all events.[/green]")
        except Exception as e:
            self.log(f"[yellow][!] Failed to set HCI filter: {e}[/yellow]")

        enable_le_scan(self.sock, enabled=True)
        
        log_handle = None
        if output_file:
            try:
                log_handle = open(output_file, "a")
                if log_handle.tell() == 0: 
                    log_handle.write("Timestamp,MAC,Model,RSSI,Status,Battery_L,Battery_R,Battery_C\n")
            except Exception as e:
                self.log(f"[red][!] Failed to open log file: {e}[/red]")

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
                                    
                                    if target_mac and mac_str.lower() != target_mac.lower():
                                        continue

                                
                                    found = self.process_data(data, mac_str, rssi)
                                    if found:
                                        self.update_display(live, found, mac_str, rssi, log_handle)
                                        if callback:
                                            # Pass full context to callback
                                            callback(mac_str, rssi, found)



        except KeyboardInterrupt:
            self.log("\n[yellow][*] Stopping Sniffer...[/yellow]")
            enable_le_scan(self.sock, enabled=False)
            if log_handle:
                log_handle.close()
                self.log(f"[green][+] Log saved to {output_file}[/green]")

    def process_data(self, data, mac_str, rssi):
        index = 0
        decoded = None
        
        while index < len(data):
            try:
                length = data[index]
                if length == 0: break
                if index + 1 + length > len(data): break
                
                ad_type = data[index+1]
                ad_data = data[index+2 : index+1+length]
                
                if ad_type == 0xFF:
                    if len(ad_data) >= 2 and ad_data[0] == 0x4C and ad_data[1] == 0x00:
                        subtype = ad_data[2]
                        payload = ad_data[3:]
                        
                        decoded = {}
                        if subtype == 0x07:
                            decoded = self.decode_proximity_packet(payload)
                        elif subtype == 0x10:
                            decoded = self.decode_proximity_packet(payload)
                            if "model" in decoded:
                                decoded["model"] = f"Nearby ({decoded['model']})"
                            else:
                                decoded["model"] = "Nearby Info"
                        else:
                            decoded = {"model": f"Apple (0x{subtype:02x})"}
                        
                        return decoded
                
                index += 1 + length
                
            except IndexError:
                break
        
        return None

    def update_display(self, live, decoded, mac_str, rssi, log_handle):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        
        bat_str = f"{decoded.get('bat_L','?')}/{decoded.get('bat_R','?')}/{decoded.get('bat_C','?')}"
        model_str = decoded.get('model', 'Unknown')
        lid_str = "Yes" if decoded.get('lid_open') else "No"
        status_raw = decoded.get('status_raw', '??')
        
        if log_handle:
            log_line = f"{now},{mac_str},{model_str},{rssi},{status_raw},{decoded.get('bat_L','?')},{decoded.get('bat_R','?')},{decoded.get('bat_C','?')}\n"
            log_handle.write(log_line)
            log_handle.flush()

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
