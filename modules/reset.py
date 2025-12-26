import os
import time

def reset_adapter(dev_id=0, console=None):
    """
    Resets the specified HCI adapter using hciconfig.
    """
    msg = f"[dim][*] Resetting hci{dev_id} to clear stale connections...[/dim]"
    if console:
        console.print(msg)
    else:
        print(msg)
        
    os.system(f"sudo hciconfig hci{dev_id} reset")
    os.system(f"sudo hciconfig hci{dev_id} up")
    time.sleep(3)
