
import sys
import os
import time
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print("Beginning Verification for Random Mode logic...")


    with patch('apybluez.hci.wrapper.start_spoof') as mock_start:
        with patch('apybluez.hci.wrapper.update_data') as mock_update:
        
 
             mock_sock = MagicMock()
             mock_start.return_value = mock_sock
             
             from modules.advertising import AdvertisingModule
             adv = AdvertisingModule()
             
          
             adv.console = MagicMock()
             adv.log = MagicMock()
             
            
             mock_sleep = MagicMock()

             mock_sleep.side_effect = [None, None, Exception("StopLoop")]
             
             with patch('time.sleep', mock_sleep):
                 print("Testing _spoof_loop with random_mode=True...")
                 try:
                    
                     adv._spoof_loop(160, None, "AirPods", False, 1, True, False, True)
                 except Exception as e:
                     if str(e) == "StopLoop":
                         print("Loop executed successfully.")
                     else:
                         print(f"Unexpected Error during loop: {e}")
                         raise e
                 
            
                 print(f"start_spoof call count: {mock_start.call_count}")
                 if mock_start.call_count >= 2:
                     print("Verified: start_spoof called multiple times (Random SAMSARA Active)")
                 else:
                     print("FAILED: start_spoof not called enough times for random mode.")
                     sys.exit(1)
                     
              
                 calls = mock_start.call_args_list
                 models_picked = []
                 for c in calls:
                   
                     if 'model_name' in c.kwargs:
                         models_picked.append(c.kwargs['model_name'])
                     elif len(c.args) > 0:
                         models_picked.append(c.args[0])
                 
                 print(f"Models picked: {models_picked}")
                 
                
                 from apybluez.apple.proximity import ProximityPairingPacket
                 raw_model = "AppleTV Setup"
                 print(f"Testing Packet Build for Raw Model: {raw_model}")
                 packet = ProximityPairingPacket.build(model_name=raw_model)
                 if b'\x4c\x00' in packet:
                     print("Verified: Raw payload packet contains Apple ID.")
                 if len(packet) > 10:
                     print("Verified: Raw payload packet has valid length.")
                 else:
                     print("FAILED: Raw payload packet too short.")
                     sys.exit(1)

    print("Verification Passed.")

except Exception as e:
    print(f"Critical Verification Error: {e}")
    sys.exit(1)
