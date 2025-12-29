import sys
import os

sys.path.append(os.getcwd())

from modules.reset import reset_adapter

def test_happy_path():
    print("Testing reset_adapter happy path...")
    try:
        reset_adapter(0)
        print("SUCCESS: reset_adapter(0) completed without error.")
    except Exception as e:
        print(f"FAILURE: reset_adapter(0) raised exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_happy_path()
