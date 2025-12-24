import unittest
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.packet_builder import PacketBuilder, ProximityPairingPacket

class TestPacketBuilder(unittest.TestCase):
    def test_proximity_pairing_packet_structure(self):
        """Test if ProximityPairingPacket builds correctly structure-wise."""

        packet = ProximityPairingPacket.build(
            model_name="AirPods Pro",
            battery_left=10,  # 100%
            battery_right=10, # 100%
            battery_case=10,  # 100%
            lid_open=True
        )
        
      
        self.assertEqual(packet[2:4], b'\x4c\x00')
        

        self.assertEqual(packet[4], 0x07)
      

        self.assertEqual(packet[5], 0x19)
        
        self.assertEqual(packet[7:9], b'\x0e\x20')
        
    def test_packet_padding(self):
        """Test if the packet has the critical padding byte for iOS."""
        packet = ProximityPairingPacket.build("AirPods Pro", 10, 10, 10, True)
    
        self.assertEqual(packet[14], 0x00)

if __name__ == '__main__':
    unittest.main()
