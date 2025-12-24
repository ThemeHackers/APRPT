import unittest
from core.packet_builder import PacketBuilder

class TestPacketBuilder(unittest.TestCase):

    def test_handshake_packet(self):
        expected = bytes.fromhex("00000400010002000000000000000000")
        self.assertEqual(PacketBuilder.build_handshake_packet(), expected)

    def test_generic_packet_structure(self):
        # Header + Opcode + Data
        # Opcode 0x1234 -> 34 12
        pkt = PacketBuilder.build_packet(0x1234, b'\xAB\xCD')
        self.assertEqual(pkt[:4], PacketBuilder.HEADER)
        self.assertEqual(pkt[4:6], b'\x34\x12')
        self.assertEqual(pkt[6:], b'\xAB\xCD')

    def test_control_command_builder(self):
        # Identifier 0x06 (Owns Connection)
        # Expected: Header + Opcode(0x0009) + Data(06 00 00 00 00)
        pkt = PacketBuilder.build_control_command(0x06)
        
        self.assertEqual(pkt[:4], PacketBuilder.HEADER)
        self.assertEqual(pkt[4:6], b'\x09\x00') # Opcode 9
        self.assertEqual(pkt[6], 0x06)          # Identifier
        self.assertEqual(len(pkt[6:]), 5)       # Payload length fixed to 5

    def test_control_command_with_args(self):
        # Identifier 0x20 (Auto Connect), Arg 0x01
        pkt = PacketBuilder.build_control_command(0x20, 0x01)
        # Payload should be 20 01 00 00 00
        self.assertEqual(pkt[6:], b'\x20\x01\x00\x00\x00')

if __name__ == '__main__':
    unittest.main()
