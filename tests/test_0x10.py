import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.packet_builder import ProximityPairingPacket

class TestPacket0x10(unittest.TestCase):
    def test_0x10_packet(self):
        """Test construction of Subtype 0x10 (Nearby Info) packets."""
        pkt = ProximityPairingPacket.build(subtype=0x10)
    
        apple_id_idx = pkt.find(b'\x4c\x00')
        self.assertNotEqual(apple_id_idx, -1, "Apple ID not found")
        
        payload_start = apple_id_idx + 2
        subtype_byte = pkt[payload_start]
        subtype_suffix = pkt[payload_start+1]
        
        print(f"Subtype Byte: {hex(subtype_byte)}")
        print(f"Suffix Byte: {hex(subtype_suffix)}")
        
        self.assertEqual(subtype_byte, 0x10, f"Expected subtype 0x10, got {hex(subtype_byte)}")
        self.assertEqual(subtype_suffix, 0x19, f"Expected suffix 0x19, got {hex(subtype_suffix)}")
        
        print("Test Passed: Subtype 0x10 packet constructed correctly.")

if __name__ == "__main__":
    unittest.main()
