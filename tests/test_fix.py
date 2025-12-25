import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.sniffer import SnifferModule

def test_apple_detection():
    print("[*] Testing Apple Device Detection Logic...\n")
    
    sniffer = SnifferModule()

    payload_simple = bytes.fromhex("1d ff 4c 00 07 19 01 02 20 54 88 56 12 76 34 56 0a 41 bb 00 00 00 00 00 00 00 00 00 00 00")
    
    print(f"Test 1: Simple Payload (Old Assumption)")
    result = sniffer.process_data(payload_simple, "00:11:22:33:44:55", -50)
    
    if result and ("Apple" in result.get('model', '') or "AirPods" in result.get('model', '')):
        print(f"  [PASS] Detected: {result['model']}")
    else:
        print(f"  [FAIL] Result: {result}")

    payload_real = bytes.fromhex("02 01 1a 1b ff 4c 00 10 06 11 1e 8d 64 2c 44 26 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
    
    print(f"\nTest 2: Real World Payload (Flags First)")
    result = sniffer.process_data(payload_real, "AA:BB:CC:DD:EE:FF", -60)
    
    if result and "Nearby" in result.get('model', ''):
        print(f"  [PASS] Detected: {result['model']}")
    else:
        print(f"  [FAIL] Result: {result}")

if __name__ == "__main__":
    test_apple_detection()
