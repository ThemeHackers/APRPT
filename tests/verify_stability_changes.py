
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from modules.advertising import AdvertisingModule
    print("Successfully imported AdvertisingModule")
    adv = AdvertisingModule()
    print("Successfully instantiated AdvertisingModule")
    
    import inspect
    sig = inspect.signature(adv.start_spoof)
    print(f"start_spoof signature: {sig}")
    
    if 'duration' in sig.parameters and 'jitter' in sig.parameters:
        print("Verified: 'duration' and 'jitter' parameters are present.")
    else:
        print("FAILED: Missing new parameters.")
        sys.exit(1)

except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
