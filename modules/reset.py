import subprocess
import time
import sys

def reset_adapter(dev_id=0, console=None):
    """
    Resets the specified HCI adapter using hciconfig.
    Strictly verifies that the interface comes back UP.
    """
    msg = f"[dim][*] Resetting hci{dev_id} to clear stale connections...[/dim]"
    if console:
        console.print(msg)
    else:
        print(msg)
        
    try:

        subprocess.run(["sudo", "hciconfig", f"hci{dev_id}", "reset"], check=True)
        subprocess.run(["sudo", "hciconfig", f"hci{dev_id}", "up"], check=True)
        
    except subprocess.CalledProcessError:
        warn_msg = f"[yellow][!] Standard reset failed for hci{dev_id}, attempting fallback (down/up)...[/yellow]"
        if console:
            console.print(warn_msg)
        else:
            print(warn_msg)
            
        try:

            subprocess.run(["sudo", "hciconfig", f"hci{dev_id}", "down"], check=True)
            time.sleep(0.5)
            subprocess.run(["sudo", "hciconfig", f"hci{dev_id}", "up"], check=True)
            
        except subprocess.CalledProcessError:
            warn_msg2 = f"[yellow][!] Down/Up failed for hci{dev_id}, attempting rfkill unblock...[/yellow]"
            if console:
                console.print(warn_msg2)
            else:
                print(warn_msg2)
                
            try:
              
                subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"], check=True)
                time.sleep(0.5)
                subprocess.run(["sudo", "hciconfig", f"hci{dev_id}", "up"], check=True)
                
            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to reset adapter hci{dev_id} after multiple attempts: {e}\nTry running 'sudo ./force_bt_reset.sh'"
                if console:
                    console.print(f"[bold red]{error_msg}[/bold red]")
                else:
                    print(error_msg)
                sys.exit(1)
    
    time.sleep(1)
    

    try:
        result = subprocess.run(
            ["hciconfig", f"hci{dev_id}"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        if "UP RUNNING" not in result.stdout:
            err = f"Interface hci{dev_id} failed to come UP after reset sequence."
            if console:
                console.print(f"[bold red]{err}[/bold red]")
            else:
                print(err)
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        err = f"Failed to check status of hci{dev_id}: {e}"
        if console:
            console.print(f"[bold red]{err}[/bold red]")
        else:
            print(err)
        sys.exit(1)

    time.sleep(1) 
