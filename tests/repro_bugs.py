
import unittest
import sys
import os


try:
    import apybluez.bluetooth as bluetooth
    from apybluez.bluetooth import _bluetooth
except ImportError:
    print("Could not import apybluez. Ensure it is installed.")
    sys.exit(1)

class TestBugFixes(unittest.TestCase):
    def test_hci_le_add_white_list_invalid_address(self):
        
        class DummySocket:
            pass
        
        sock = DummySocket()
        
       
        with self.assertRaisesRegex(ValueError, "Invalid address"):
             _bluetooth.hci_le_add_white_list(sock, "", 0, 0)

    def test_module_has_constants(self):
        self.assertTrue(hasattr(bluetooth, 'HCI'))
        self.assertTrue(hasattr(bluetooth, 'L2CAP'))

if __name__ == '__main__':
    unittest.main()
