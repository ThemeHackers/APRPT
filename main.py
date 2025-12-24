import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from core.connection import AAPConnection
from modules.recon import ReconModule
from modules.hijack import HijackModule
from modules.denial_of_service import DoSModule

# Initialize Rich Console
console = Console()

def print_banner():
    banner_text = Text("Apple Protocol Research & Pentest Tool (APRPT)", style="bold white on blue", justify="center")
    console.print(Panel(banner_text, border_style="blue", expand=False))
    console.print("[dim]v1.0.0 - PoC by ThemeHackers[/dim]", justify="center")
    console.print()

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="APRPT - Apple Bluetooth Low Energy Pentest Tool")
    parser.add_argument("-t", "--target", help="Target MAC Address (Required for recon/hijack/dos)")
    parser.add_argument("-m", "--mode", help="Mode: recon, hijack, dos, advertise, honeypot", choices=["recon", "hijack", "dos", "advertise", "honeypot"], required=True)
    parser.add_argument("-M", "--model", help="Spoof Model Name (e.g. 'AirPods Pro') or ID for advertise mode.")

    args = parser.parse_args()
    target_mac = args.target
    mode = args.mode
    
    console.print(f"[*] Mode: [bold cyan]{mode}[/bold cyan]")

    try:
        import bluetooth._bluetooth as bluez
        sock = bluez.hci_open_dev(0)
        sock.close()
        console.print("[green][+][/green] Bluetooth Hardware (hci0) detected successfully.")
    except ImportError:
        if sys.platform == 'linux':
             console.print("[red][!][/red] Error: 'pybluez' not installed or not working.")
        else:
             console.print("[yellow][!][/yellow] Warning: 'pybluez' not found. This is expected on non-Linux systems.")
    except Exception as e:
        console.print(f"[yellow][!][/yellow] Warning: Unable to open Bluetooth device hci0: {e}")
        console.print("[yellow][!][/yellow] Ensure your Ugreen adapter is plugged in and recognized as hci0.")
        if mode != "advertise" and mode != "honeypot":
             pass

    if mode == "advertise":
        from modules.advertising import AdvertisingModule
        from rich.table import Table
        
        module = AdvertisingModule(console=console)
        
        # Determine payload
        payload = None
        model_name = "AirPods (Default)"
        
        # Dictionary from module
        device_data = AdvertisingModule.DEVICE_DATA

        if args.model:
            # Try to match ID or Name
            found_id = None
            if args.model.isdigit():
                if int(args.model) in device_data:
                    found_id = int(args.model)
            else:
                for k, v in device_data.items():
                    if v['name'].lower() == args.model.lower():
                        found_id = k
                        break
            
            if found_id:
                payload = device_data[found_id]['data']
                model_name = device_data[found_id]['name']
            else:
                 console.print(f"[red][!] Model '{args.model}' not found. Using default.[/red]")
        else:
            # Interactive Menu
            table = Table(title="Available Spoof Models", show_header=True, header_style="bold magenta")
            table.add_column("ID", style="cyan", width=4)
            table.add_column("Device Name", style="white")
            
            # Sort by ID
            for dev_id in sorted(device_data.keys()):
                table.add_row(str(dev_id), device_data[dev_id]['name'])
            
            console.print(table)
            console.print("[bold yellow]Choose a model ID (default=1):[/bold yellow] ", end="")
            try:
                choice = input().strip()
                if not choice:
                    choice = "1"
                
                if choice.isdigit() and int(choice) in device_data:
                    payload = device_data[int(choice)]['data']
                    model_name = device_data[int(choice)]['name']
                else:
                    console.print("[red][!] Invalid selection. Using default.[/red]")
            except KeyboardInterrupt:
                sys.exit(0)
                
        module.start_spoof(custom_payload=payload, model_name=model_name)
        return

    if mode == "honeypot":
        from modules.honeypot import HoneyPotModule
        module = HoneyPotModule(console=console)
        module.start_honeypot()
        return

    if not target_mac:
        console.print("[red][!] Error: Target MAC (-t) is required for recon, hijack, and dos modes.[/red]")
        sys.exit(1)
    
    console.print(f"[*] Target: [bold yellow]{target_mac}[/bold yellow]")
    
    conn = AAPConnection(target_mac, console=console)
    if not conn.connect():
        console.print("[red][!] Failed to establish connection. Exiting.[/red]")
        sys.exit(1)
        
    try:
        if mode == "recon":
            module = ReconModule(conn, console=console)
            module.get_device_info()
            
        elif mode == "hijack":
            module = HijackModule(conn, console=console)
            module.run_smart_routing_hijack()
            
        elif mode == "dos":
            module = DoSModule(conn, console=console)
            module.start_flood()
            
    except KeyboardInterrupt:
        console.print("\n[yellow][!] User interrupted.[/yellow]")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
