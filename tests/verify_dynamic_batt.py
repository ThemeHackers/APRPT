
import sys
import os
import time
from unittest.mock import MagicMock


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from modules.advertising import AdvertisingModule
    print("Successfully imported AdvertisingModule")
    
    import modules.advertising as adv_mod
    adv_mod.start_spoof = MagicMock(return_value=MagicMock())
    adv_mod.stop_spoof = MagicMock()
    adv_mod.reset_adapter = MagicMock()
    

    adv = AdvertisingModule()
    

    import inspect
    sig = inspect.signature(adv.start_spoof)
    if 'dynamic_batt' in sig.parameters:
        print("Verified: 'dynamic_batt' parameter is present module.")
    else:
        print("FAILED: Missing 'dynamic_batt' parameter.")
        sys.exit(1)

    print("Syntax verification passed.")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
