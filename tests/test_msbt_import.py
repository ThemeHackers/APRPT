
import sys
import os

print(f"Platform: {sys.platform}")

try:
    from bluetooth import msbt
    print("SUCCESS: Imported bluetooth.msbt (Unexpected on Linux)")
except ImportError as e:
    print(f"EXPECTED ERROR: Could not import msbt: {e}")
except Exception as e:
    print(f"ERROR: {e}")

try:
    import bluetooth._msbt
    print("SUCCESS: Imported bluetooth._msbt (Unexpected on Linux)")
except ImportError as e:
    print(f"EXPECTED ERROR: Could not import bluetooth._msbt: {e}")
