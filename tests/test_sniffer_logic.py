import unittest
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.sniffer import SnifferModule

class TestSnifferLogic(unittest.TestCase):
    def setUp(self):

        self.sniffer = SnifferModule(console=None)

        fake_data = bytes.fromhex("19010e2001aaa001" + "00"*20)
        
        info = self.sniffer.decode_proximity_packet(fake_data)
        
        self.assertIn("AirPods Pro", info['model'])
        self.assertIn("!!! SPOOF DETECTED !!!", info['model'])
        self.assertEqual(info['bat_L'], "100%")
        self.assertEqual(info['bat_R'], "100%")

        self.assertEqual(info['bat_C'], "100%")
        self.assertTrue(info['lid_open'])

    def test_spoof_detection(self):
        """Test logic for detecting spoofed packets (Pairing bit)."""
       
        pass

if __name__ == '__main__':
    unittest.main()
