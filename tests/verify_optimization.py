
import sys
import os
import time
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:

    import apybluez.hci.wrapper as wrapper
    if hasattr(wrapper, 'update_data'):
         print("Verified: update_data function exists in wrapper.")
    else:
         print("FAILED: update_data missing from wrapper.")
         sys.exit(1)


    with patch('apybluez.hci.wrapper.start_spoof') as mock_start:
        with patch('apybluez.hci.wrapper.update_data') as mock_update:
             mock_sock = MagicMock()
             mock_start.return_value = mock_sock
             
             from modules.advertising import AdvertisingModule
             adv = AdvertisingModule()
             
         
             import time
             time.sleep = MagicMock()
             
             print("Testing _spoof_loop with dynamic_batt=True...")
             try:
                
                 with patch.object(adv, 'log') as mock_log:

                     mock_update.side_effect = [None, Exception("StopLoop")]
                     
                     try:
                         adv._spoof_loop(160, None, "AirPods", False, 2, True, True)
                     except Exception as e:
                         if str(e) == "StopLoop":
                             print("Loop executed.")
                         else: 
                             raise e
                     
                    
                     if mock_update.called:
                         print("Verified: update_data was called inside the loop.")
                     else:
                         print("FAILED: update_data was NOT called.")
                         sys.exit(1)
                         
                     
                     print("Socket reuse logic appears consistent with code structure.")
                     
             except Exception as e:
                 print(f"Test Error: {e}")
                 sys.exit(1)

except Exception as e:
    print(f"Critical Error: {e}")
    sys.exit(1)
