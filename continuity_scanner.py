import struct
import sys
import argparse
import time
import apybluez.bluetooth as bluetooth
import apybluez.bluetooth._bluetooth as _bt
from rich.console import Console
from rich.theme import Theme
from rich.live import Live
from rich.table import Table

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "green",
    "device": "bold white",
    "type": "bold yellow"
})
console = Console(theme=custom_theme)

CM_TYPES = {
    0x03: "AirPrint",
    0x05: "AirDrop",
    0x06: "HomeKit",
    0x07: "Proximity Pairing",
    0x08: "Hey Siri",
    0x0B: "Magic Switch",
    0x0C: "Handoff",
    0x10: "Nearby Info"
}

OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_ENABLE = 0x000C
OCF_LE_SET_SCAN_PARAMETERS = 0x000B

def parse_continuity_message(cm_type, cm_data):
    details = ""
    if cm_type == 0x05 and len(cm_data) >= 18:
        details = f"[dim]V:{cm_data[8]:02x} ID:{cm_data[9:11].hex()} Ph:{cm_data[11:13].hex()}[/dim]"
    elif cm_type == 0x08 and len(cm_data) >= 4:
        details = f"[dim]Hash:{cm_data[0:2].hex()} SNR:{cm_data[2]} Conf:{cm_data[3]}[/dim]"
    elif cm_type == 0x0C:
        if len(cm_data) >= 2:
            details = f"[dim]IV:{cm_data[:2].hex()} Enc:{cm_data[2:].hex()}[/dim]"
    elif cm_type == 0x10 and len(cm_data) >= 1:
        details = f"[dim]Activity: 0x{cm_data[0]:02x}[/dim]"
    return details

def resolve_filter_types(type_args):
    if not type_args:
        return None
    allowed_ids = set()
    name_map = {name.lower().replace(" ", ""): pid for pid, name in CM_TYPES.items()}
    
    for arg in type_args:
        arg_clean = arg.lower().replace(" ", "")
        if arg_clean in name_map:
            allowed_ids.add(name_map[arg_clean])
            continue
        try:
            pid = int(arg, 0)
            allowed_ids.add(pid)
        except ValueError:
            pass
    return allowed_ids

def generate_table(devices):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Address", style="device", width=18)
    table.add_column("RSSI", justify="right", width=6)
    table.add_column("Type", style="type", width=30) 
    table.add_column("Last Seen", width=10)
    table.add_column("Details")

    current_time = time.time()
    for addr, info in devices.items():
        time_diff = current_time - info['timestamp']
        table.add_row(
            addr,
            f"{info['rssi']}dBm",
            info['type_display'],
            f"{time_diff:.1f}s",
            info['details']
        )
    return table

def main():
    parser = argparse.ArgumentParser(description="Apple Continuity Scanner")
    parser.add_argument("-t", "--types", nargs="+", help="Filter by message type")
    parser.add_argument("--list-types", action="store_true", help="List all known continuity types")
    args = parser.parse_args()

    if args.list_types:
        for pid, name in CM_TYPES.items():
            console.print(f"0x{pid:02x}: {name}")
        sys.exit(0)

    filter_ids = resolve_filter_types(args.types)
    
    dev_id = 0
    try:
        sock = _bt.hci_open_dev(dev_id)
    except Exception as e:
        console.print(f"[danger]Error: {e}[/danger]")
        sys.exit(1)

    flt = _bt.hci_filter_new()
    _bt.hci_filter_set_ptype(flt, _bt.HCI_EVENT_PKT)
    _bt.hci_filter_set_event(flt, 0x3E)
    sock.setsockopt(_bt.SOL_HCI, _bt.HCI_FILTER, flt)

    try:
        scan_params = struct.pack("<BHHBB", 0x01, 0x0010, 0x0010, 0x00, 0x00)
        _bt.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_PARAMETERS, scan_params)
        cmd_pkt = struct.pack("<BB", 0x01, 0x00) 
        _bt.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)
    except Exception as e:
        console.print(f"[danger]Failed to enable LE scan: {e}[/danger]")

    sock.settimeout(0.1) 
    
    devices = {} 

    try:
        with Live(generate_table(devices), console=console, refresh_per_second=4, screen=False) as live:
            while True:
                try:
                    pkt = sock.recv(255)
                except _bt.timeout:
                    live.update(generate_table(devices))
                    continue
                except Exception:
                    break

                ptype, event, plen = struct.unpack("BBB", pkt[:3])
                
                if event == 0x3E: 
                    subevent = pkt[3]
                    if subevent == 0x02: 
                        num_reports = pkt[4]
                        offset = 5
                        
                        for i in range(num_reports):
                            if offset >= len(pkt): break
                            
                            addr = pkt[offset+2 : offset+8]
                            addr_str = ':'.join(f'{b:02x}' for b in reversed(addr))
                            
                            data_len = pkt[offset+8]
                            data_hex = pkt[offset+9 : offset+9+data_len]
                            rssi = pkt[offset+9+data_len] if offset+9+data_len < len(pkt) else 0
                            rssi_val = rssi - 256
                            
                            j = 0
                            while j < len(data_hex):
                                if j + 1 >= len(data_hex): break
                                length = data_hex[j]
                                if length == 0: break
                                
                                ad_type = data_hex[j+1]
                                ad_data = data_hex[j+2 : j+1+length]
                                
                                if ad_type == 0xFF: 
                                    if len(ad_data) >= 2 and ad_data[:2] == b'\x4c\x00':
                                        payload = ad_data[2:]
                                        
                                        k = 0
                                        while k < len(payload):
                                            if k + 1 >= len(payload): break
                                            cm_type = payload[k]
                                            cm_len = payload[k+1]
                                            
                                            if k + 2 + cm_len > len(payload): break
                                            cm_data = payload[k+2 : k+2+cm_len]
                                            
                                            if filter_ids is not None and cm_type not in filter_ids:
                                                k += 2 + cm_len
                                                continue

                                            type_name = CM_TYPES.get(cm_type, f"Unknown (0x{cm_type:02x})")
                                            details = parse_continuity_message(cm_type, cm_data)
                                                                            
                                            if addr_str not in devices:
                                                devices[addr_str] = {
                                                    'rssi': rssi_val,
                                                    'seen_types': {type_name},
                                                    'type_display': type_name,
                                                    'details': details,
                                                    'timestamp': time.time()
                                                }
                                            else:
                                                dev = devices[addr_str]
                                                dev['rssi'] = rssi_val
                                                dev['timestamp'] = time.time()
                                                dev['seen_types'].add(type_name)
                                                
                                                full_types = sorted(list(dev['seen_types']))
                                                dev['type_display'] = ", ".join(full_types)

                                                if details or not dev['details']:
                                                    dev['details'] = details

                                            sorted_devices = dict(sorted(devices.items(), key=lambda item: item[1]['timestamp'], reverse=True))
                                            sorted_devices = dict(sorted(devices.items(), key=lambda item: item[1]['timestamp'], reverse=True))
                                            devices = sorted_devices

                                            k += 2 + cm_len
                                
                                j += 1 + length

                            offset += 9 + data_len + 1
                
                live.update(generate_table(devices))

    except KeyboardInterrupt:
        pass
    finally:
        try:
            cmd_pkt = struct.pack("<BB", 0x00, 0x00) 
            _bt.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)
        except (Exception, KeyboardInterrupt):
            pass
        console.print("[warning]Scanner stopped.[/warning]")

if __name__ == "__main__":
    main()