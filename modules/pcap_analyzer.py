import sys
import os
import argparse
from scapy.all import *
from scapy.layers.bluetooth import *
from scapy.layers.bluetooth4LE import *
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()

HCI_COMMANDS = {
    0x2005: "LE_Set_Random_Address",
    0x2006: "LE_Set_Advertising_Parameters",
    0x2008: "LE_Set_Advertising_Data",
    0x2009: "LE_Set_Scan_Response_Data",
    0x200A: "LE_Set_Advertise_Enable",
    0x200B: "LE_Set_Scan_Parameters",
    0x200C: "LE_Set_Scan_Enable",
    0x200D: "LE_Create_Connection",
}

AAP_OPCODES = {
    0x0004: "Battery Status Report",
    0x0009: "Noise Control (ANC/Transparency)",
    0x000F: "Subscribe to Notifications",
    0x0017: "Head Tracking Control",
    0x001A: "Rename Device",
    0x004D: "Feature Unlock (Adaptive/Conversation)",
}


PROXIMITY_PAIRING_TYPE = 0x07

class PcapAnalyzer:
    def __init__(self, pcap_path, verbose=False):
        self.pcap_path = pcap_path
        self.verbose = verbose
        if pcap_path and not os.path.exists(pcap_path):
            console.print(f"[bold red][!] File not found: {pcap_path}[/bold red]")
            sys.exit(1)

    def analyze(self):
        console.print(f"[bold blue][*] Loading and analyzing {self.pcap_path}... Please wait.[/bold blue]")
        
        try:
            packets = rdpcap(self.pcap_path)
        except Exception as e:
            console.print(f"[bold red][!] Error reading PCAP: {e}[/bold red]")
            return

        total_packets = len(packets)
        ble_packets = 0
        adv_packets = 0
        conn_reqs = 0
        victims = []

        if self.verbose:
            console.print(f"\n[bold underline]Detailed Packet Inspection[/bold underline]")

        for i, pkt in enumerate(packets):
            is_ble = HCI_Hdr in pkt or BTLE in pkt
            if not is_ble:
                continue

            if self.verbose:
                pkt_tree = Tree(f"[bold yellow]Packet #{i+1}[/bold yellow]")
                header_node = pkt_tree.add("[bold blue][HEADER][/bold blue]")
                opcode_node = pkt_tree.add("[bold green][OPCODE/EVENT][/bold green]")
                data_node = pkt_tree.add("[bold magenta][DATA][/bold magenta]")

            if HCI_Hdr in pkt:
                ble_packets += 1
                hci_type = pkt[HCI_Hdr].type
                
                if self.verbose:
                    type_str = "Unknown"
                    if hci_type == 1: type_str = "Command (0x01)"
                    elif hci_type == 2: type_str = "ACL Data (0x02)"
                    elif hci_type == 3: type_str = "SCO Data (0x03)"
                    elif hci_type == 4: type_str = "Event (0x04)"
                    header_node.add(f"Type: {type_str}")

                if HCI_Command_Hdr in pkt:
                    opcode = pkt[HCI_Command_Hdr].opcode
                    cmd_name = HCI_COMMANDS.get(opcode, "Unknown HCI Command")
                    if self.verbose:
                        opcode_node.add(f"Command Opcode: {hex(opcode)} ({cmd_name})")

                if HCI_Event_Hdr in pkt:
                    code = pkt[HCI_Event_Hdr].code
                    if self.verbose:
                        opcode_node.add(f"Event Code: {hex(code)}")
                    
                    if code == 0x3E: 
                         if HCI_Event_LE_Meta in pkt:
                            subevent = pkt[HCI_Event_LE_Meta].event
                            if self.verbose:
                                opcode_node.add(f"  LE SubEvent: {hex(subevent)}")
                                if subevent == 1: opcode_node.add("  -> LE Connection Complete")
                                if subevent == 2: opcode_node.add("  -> LE Advertising Report")

                if hci_type == 2 and self.verbose:
                     raw_acl = bytes(pkt[HCI_Hdr].payload)
                     if raw_acl.startswith(b'\x04\x00\x04\x00'):
                         opcode_node.add(f"[bold red]AAP PROTOCOL DETECTED![/bold red]")
                         try:
                             aap_opcode = struct.unpack("<H", raw_acl[4:6])[0]
                             aap_name = AAP_OPCODES.get(aap_opcode, "Unknown AAP Command")
                             opcode_node.add(f"AAP Opcode: {hex(aap_opcode)} ({aap_name})")
                         except:
                             pass

            if BTLE in pkt:
                ble_packets += 1
                if self.verbose:
                    header_node.add(f"Layer: Bluetooth LE (Link Layer)")
                
                if BTLE_ADV_IND in pkt:
                    adv_packets += 1
                    if self.verbose:
                        opcode_node.add("PDU: ADV_IND (Advertising Indication)")
                        if hasattr(pkt[BTLE_ADV_IND], "TxAdd"):
                             header_node.add(f"TxAdd: {pkt[BTLE_ADV_IND].TxAdd} (Random)" if pkt[BTLE_ADV_IND].TxAdd else "TxAdd: Public")
                        
                        try:
                             raw_bytes = bytes(pkt[BTLE_ADV_IND])
                             if b'\xff\x4c\x00' in raw_bytes:
                                 offset = raw_bytes.find(b'\xff\x4c\x00')
                                 data_start = offset + 3 
                                 
                                 if len(raw_bytes) > data_start and raw_bytes[data_start] == 0x07:
                                     prox_node = data_node.add("[bold cyan]Apple Proximity Pairing Data[/bold cyan]")
                                     
                                     pp_data = raw_bytes[data_start:]
                                     if len(pp_data) >= 10:
                                         model_id = struct.unpack(">H", pp_data[3:5])[0]
                                         status_byte = pp_data[5]
                                         pods_batt = pp_data[6]
                                         case_batt = pp_data[7]
                                         lid_byte = pp_data[8]
                                         
                                         model_map = {0x0E20: "AirPods Pro", 0x1420: "AirPods Pro 2", 0x0A20: "AirPods Max"}
                                         model_name = model_map.get(model_id, f"Unknown ({hex(model_id)})")
                                         
                                         left_batt_val = (pods_batt >> 4) & 0xF
                                         right_batt_val = pods_batt & 0xF
                                         case_batt_val = (case_batt >> 4) & 0xF
                                         
                                         def fmt_batt(v): return "100%" if v >= 0xA else f"{v*10}%"
                                         
                                         prox_node.add(f"Model: {model_name}")
                                         prox_node.add(f"Battery: L={fmt_batt(left_batt_val)}, R={fmt_batt(right_batt_val)}, Case={fmt_batt(case_batt_val)}")
                                         
                                         lid_open = (lid_byte & 0x08) == 0 
                                         prox_node.add(f"Lid State: {'[green]OPEN[/green]' if lid_open else '[red]CLOSED[/red]'}")
                        except Exception as e:
                             pass
=

            if self.verbose:
                try:
                    raw_data = bytes(pkt)
                    hex_str = ' '.join(f'{b:02x}' for b in raw_data)
                    if len(hex_str) > 60:
                        hex_str = hex_str[:60] + "... (truncated)"
                    data_node.add(f"Raw Hex: {hex_str}")
                except:
                    data_node.add("Could not extract raw data")
                
                console.print(pkt_tree)
                console.print("")

        table = Table(title=f"Analysis Results: {os.path.basename(self.pcap_path)}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Packets", str(total_packets))
        table.add_row("BLE Packets (Est)", str(ble_packets))
        table.add_row("Connection Requests", f"[bold red]{conn_reqs}[/bold red]" if conn_reqs > 0 else "0")
        
        console.print(table)
        
        if conn_reqs > 0:
            console.print(Panel("[bold red]VICTIM DETECTED![/bold red]\nFound valid CONNECT_REQ packets indicating a device attempted to pair.", title="Security Alert"))
            for v in victims:
                console.print(f" - Initiator (Victim): [yellow]{v['initiator']}[/yellow] -> Advertiser (HoneyPot): [blue]{v['advertiser']}[/blue]")
        elif self.verbose:
            console.print("[dim][*] No definitive connection requests found in this capture.[/dim]")

def show_definitions():
    table = Table(title="Known Bluetooth & AAP Definitions", show_header=True, header_style="bold magenta")
    table.add_column("Protocol", style="cyan", width=12)
    table.add_column("Opcode", style="green", width=10)
    table.add_column("Description", style="white")


    for op, name in HCI_COMMANDS.items():
        table.add_row("HCI (BLE)", hex(op), name)
    

    table.add_section()
    for op, name in AAP_OPCODES.items():
        table.add_row("AAP (Apple)", hex(op), f"[italic]{name}[/italic]")
    

    table.add_row("AAP (Adv)", "0x07", "[italic]Proximity Pairing Message (Status/Battery)[/italic]")

    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="APRPT PCAP Analyzer")
    parser.add_argument("-f", "--file", help="Path to PCAPNG file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable detailed packet inspection")
    parser.add_argument("--definitions", action="store_true", help="Show opcode definitions table")
    
    args = parser.parse_args()

    if args.definitions:
        show_definitions()
        return

    if not args.file:
       
        if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
           
             args.file = sys.argv[1]
        else:
            parser.print_help()
            return
    
    analyzer = PcapAnalyzer(args.file, verbose=args.verbose)
    analyzer.analyze()

if __name__ == "__main__":
    main()
