import sys
import os
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from core.connection import AAPConnection
from modules.recon import ReconModule
from modules.hijack import HijackModule
from modules.denial_of_service import DoSModule
from modules.control import ControlModule

console = Console()

def print_banner():
    banner_text = Text("Apple Protocol Research & Pentest Tool (APRPT)", style="bold white on blue", justify="center")
    console.print(Panel(banner_text, border_style="blue", expand=False))
    console.print("[dim]v1.0.0 - PoC by ThemeHackers[/dim]", justify="center")
    console.print()

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="APRPT - Apple Bluetooth Low Energy Pentest Tool")
    if len(sys.argv) == 1:
        interactive_mode()
    
    parser.add_argument("-t", "--target", help="Target MAC Address (Required for recon/hijack/dos/control)")
    parser.add_argument("-m", "--mode", help="Mode: recon, hijack, dos, advertise, honeypot, sniff, bleed, control, analyze", choices=["recon", "hijack", "dos", "advertise", "honeypot", "sniff", "bleed", "control", "analyze"])
    parser.add_argument("-M", "--model", help="Spoof Model Name (e.g. 'AirPods Pro') or ID for advertise mode.")
    parser.add_argument("--log-file", help="Output file for Pattern of Life logs (sniff mode)")
    parser.add_argument("--phishing", action="store_true", help="Enable Phishing Mode (Cycle all models) for advertise mode")
    parser.add_argument("-f", "--file", help="PCAPNG file path for analysis (Required for analyze mode)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable detailed packet inspection (analyze mode)")
    parser.add_argument("--definitions", action="store_true", help="Show opcode definitions table")

    if os.geteuid() != 0:
        console.print("[red][!] WARNING: Not running as root. APRPT requires sudo for Bluetooth operations.[/red]")
        console.print("[red][!] usage: sudo python3 main.py ...[/red]")

    args_parsed = False
    if len(sys.argv) > 1:

        if "--definitions" in sys.argv:
             from modules.pcap_analyzer import show_definitions
             show_definitions()
             sys.exit(0)

        args = parser.parse_args()
        args_parsed = True

    try:
        if args_parsed:
            run_cli_mode(args)
        else:
            interactive_mode()
    except PermissionError:
        console.print("\n[bold red][!] Permission Denied: Please run as root (sudo).[/bold red]")
        sys.exit(1)
    except Exception as e:
        if "Operation not permitted" in str(e):
             console.print("\n[bold red][!] Bluetooth Error: Operation not permitted.[/bold red]")
             console.print("[bold red][!] Please run as root: sudo python3 main.py ...[/bold red]")
             sys.exit(1)
        raise e

def run_cli_mode(args):
    target_mac = args.target
    mode = args.mode
    
    console.print(f"[*] Mode: [bold cyan]{mode}[/bold cyan]")
    
    check_hardware(mode)

    if mode == "advertise":
        from modules.advertising import AdvertisingModule
        from rich.table import Table
        
        module = AdvertisingModule(console=console)
        device_data = AdvertisingModule.DEVICE_DATA

        if args.phishing:
            module.start_spoof(phishing_mode=True)
            return

        if args.model:
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
                model_name = device_data[found_id]['name']
                module.start_spoof(model_name=model_name)
            else:
                 console.print(f"[red][!] Model '{args.model}' not found. Using default.[/red]")
        else:
             
            table = Table(title="Available Spoof Models", show_header=True, header_style="bold magenta")
            table.add_column("ID", style="cyan", width=4)
            table.add_column("Device Name", style="white")
            for dev_id in sorted(device_data.keys()):
                table.add_row(str(dev_id), device_data[dev_id]['name'])
            console.print(table)
            console.print("[bold yellow]Choose a model ID (default=1):[/bold yellow] ", end="")
            try:
                choice = input().strip() or "1"
                if choice.isdigit() and int(choice) in device_data:
                     module.start_spoof(model_name=device_data[int(choice)]['name'])
                else:
                     console.print("[red][!] Invalid. Defaulting.[/red]")
                     module.start_spoof(model_name="AirPods")
            except KeyboardInterrupt:
                return

    elif mode == "honeypot":
        from modules.honeypot import HoneyPotModule
        module = HoneyPotModule(console=console)
        module.start_honeypot()

    elif mode == "sniff":
        from modules.sniffer import SnifferModule
        module = SnifferModule(console=console)
        module.start_sniff(target_mac=target_mac, output_file=args.log_file)

    elif mode == "bleed":
        from modules.fuzzer import FuzzerModule
        module = FuzzerModule(console=console)
        if target_mac:
             module.start_protocol_fuzzing(target_mac)
        else:
             module.start_bleed()
             
    elif mode == "analyze":
        if not args.file:
            console.print("[red][!] Error: --file (-f) is required for analysis mode.[/red]")
            return
        from modules.pcap_analyzer import PcapAnalyzer
        analyzer = PcapAnalyzer(args.file, verbose=args.verbose)
        analyzer.analyze()

    elif mode == "control":
        from modules.control import ControlModule
        module = ControlModule(console=console, target=target_mac)
        module.start_control()

    else:
        if not target_mac:
            console.print("[red][!] Error: Target MAC (-t) is required.[/red]")
            return
        
        console.print(f"[*] Target: [bold yellow]{target_mac}[/bold yellow]")
        
      
        if mode == "dos":
             from modules.denial_of_service import DoSModule
          
             conn = AAPConnection(target_mac, console=console) 
             module = DoSModule(conn, console=console)
             module.l2cap_flood(target_mac)
             return

        conn = AAPConnection(target_mac, console=console)
        if not conn.connect():
            console.print("[red][!] Failed to establish connection. Exiting.[/red]")
            return
            
        try:
            if mode == "recon":
                module = ReconModule(conn, console=console)
                module.get_device_info()
            elif mode == "hijack":
                module = HijackModule(conn, console=console)
                module.run_smart_routing_hijack()
        except KeyboardInterrupt:
            console.print("\n[yellow][!] User interrupted.[/yellow]")
        finally:
            conn.close()

def check_hardware(mode):
    try:
        import bluetooth._bluetooth as bluez
        sock = bluez.hci_open_dev(0)
        sock.close()
        console.print("[green][+][/green] Bluetooth Hardware (hci0) detected.")
    except Exception as e:
        console.print(f"[yellow][!][/yellow] Warning: Hardware check failed: {e}")
        if mode not in ["advertise", "honeypot", "sniff", "bleed"]:
             pass 

def interactive_mode():
    console.print("[bold green]ENTERING INTERACTIVE MODE[/bold green]")
    console.print("Type 'help' for commands.")
    
    current_module = None
    target_mac = None
    spoof_model_name = "AirPods Pro" 
    
    from modules.advertising import AdvertisingModule
    device_data = AdvertisingModule.DEVICE_DATA

    while True:
        try:
            prompt = "[aprpt"
            if current_module:
                prompt += f" ({current_module})"
            prompt += "] > "
            
            cmd_line = input(prompt).strip().split()
            if not cmd_line:
                continue
                
            cmd = cmd_line[0].lower()
            args = cmd_line[1:]
            
            if cmd == "help":
                console.print(Panel("""
[bold]Commands:[/bold]
  use <module>      : Select module (recon, hijack, dos, advertise, honeypot, sniff, bleed)
  set target <mac>  : Set Target MAC (for recon, hijack, dos)
  set model <id>    : Set Spoof Model (for advertise)
  show options      : Show current settings
  show models       : List available spoof models
  run               : Execute the selected module
  exit              : Exit APRPT
""", title="Help Menu"))

            elif cmd == "exit":
                console.print("Goodbye!")
                break
                
            elif cmd == "use":
                if not args:
                    console.print("[red]Usage: use <module>[/red]")
                    continue
                valid_mods = ["recon", "hijack", "dos", "advertise", "honeypot", "sniff", "bleed", "control"]
                if args[0] in valid_mods:
                    current_module = args[0]
                    console.print(f"[*] switched to [bold cyan]{current_module}[/bold cyan]")
                else:
                     console.print(f"[red]Invalid module. Choices: {', '.join(valid_mods)}[/red]")
                     
            elif cmd == "set":
                if len(args) < 2:
                     console.print("[red]Usage: set <param> <value>[/red]")
                     continue
                param = args[0].lower()
                val = args[1]
                
                if param == "target":
                    target_mac = val
                    console.print(f"[*] Target => {target_mac}")
                elif param == "model":
                    if val.isdigit() and int(val) in device_data:
                        spoof_model_name = device_data[int(val)]['name']
                        console.print(f"[*] Model => {spoof_model_name}")
                    else:
                        console.print("[red]Invalid Model ID. Use 'show models' to see list.[/red]")
                else:
                    console.print("[red]Unknown parameter.[/red]")
                    
            elif cmd == "show":
                if not args: continue
                sub = args[0].lower()
                if sub == "options":
                    console.print(f"Module: {current_module or 'None'}")
                    console.print(f"Target: {target_mac or 'None'}")
                    console.print(f"Spoof Model: {spoof_model_name}")
                elif sub == "models":
                    from rich.table import Table
                    t = Table(title="Spoof Models")
                    t.add_column("ID")
                    t.add_column("Name")
                    for k in sorted(device_data.keys()):
                        t.add_row(str(k), device_data[k]['name'])
                    console.print(t)
                    
            elif cmd == "run" or cmd == "exploit":
                if not current_module:
                    console.print("[red]No module selected. Use 'use <module>'[/red]")
                    continue
                
                
                args_mock = type('Args', (), {})()
                args_mock.mode = current_module
                args_mock.target = target_mac
                args_mock.model = None
                
                check_hardware(current_module)
                
                try:
                    if current_module == "advertise":
                        from modules.advertising import AdvertisingModule
                        mod = AdvertisingModule(console=console)
                        mod.start_spoof(model_name=spoof_model_name)
                        
                    elif current_module == "honeypot":
                        from modules.honeypot import HoneyPotModule
                        mod = HoneyPotModule(console=console)
                        mod.start_honeypot()

                    elif current_module == "sniff":
                        from modules.sniffer import SnifferModule
                        mod = SnifferModule(console=console)
                        mod.start_sniff()

                    elif current_module == "bleed":
                        from modules.fuzzer import FuzzerModule
                        mod = FuzzerModule(console=console)
                        if target_mac:
                             mod.start_protocol_fuzzing(target_mac)
                        else:
                             mod.start_bleed()
                        
                    elif current_module == "control":
                        from modules.control import ControlModule
                        if not target_mac:
                             console.print("[red][!] Target required. 'set target <MAC>'[/red]")
                             continue
                        mod = ControlModule(console=console, target=target_mac)
                        mod.start_control()
                        
                    else:
                        if not target_mac:
                             console.print("[red][!] Target required. 'set target <MAC>'[/red]")
                             continue
                        
                        conn = AAPConnection(target_mac, console=console)
                        if conn.connect():
                            try:
                                if current_module == "recon":
                                    ReconModule(conn, console).get_device_info()
                                elif current_module == "hijack":
                                    HijackModule(conn, console).run_smart_routing_hijack()
                                elif current_module == "dos":
                                    DoSModule(conn, console).l2cap_flood(target_mac)
                            finally:
                                conn.close()
                                
                except KeyboardInterrupt:
                    console.print("\n[yellow]Interrupted.[/yellow]")
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")

            else:
                console.print("[red]Unknown command. Type 'help'.[/red]")
                
        except KeyboardInterrupt:
            console.print("\nType 'exit' to quit.")

if __name__ == "__main__":
    main()
