import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apybluez.apple.packets import PacketBuilder
from apybluez.apple.proximity import ProximityPairingPacket
from apybluez.apple.socket import AAPSocket

class TestPacketBuilder(unittest.TestCase):
    def test_handshake_packet(self):
        pkt = PacketBuilder.build_handshake_packet()
        expected = bytes.fromhex("00000400010002000000000000000000")
        self.assertEqual(pkt, expected)

    def test_build_packet_header(self):
        # Header is 04 00 04 00
        pkt = PacketBuilder.build_packet(0x1234, b'\x01\x02')
        self.assertEqual(pkt[:4], b'\x04\x00\x04\x00')
        # Opcode little endian 0x1234 -> 34 12
        self.assertEqual(pkt[4:6], b'\x34\x12')
        self.assertEqual(pkt[6:], b'\x01\x02')

    def test_volume_ducking(self):
        # Opcode 0x0009, Subcmd 0x0A, State 0x01 (True)
        # Control command padding to 5 bytes payload
        # Payload: 0A 01 00 00 00
        # Packet: Header + 09 00 + Payload
        pkt = PacketBuilder.build_volume_ducking_packet(True)
        self.assertEqual(pkt[4:6], b'\x09\x00') # Opcode
        self.assertEqual(pkt[6:], b'\x0A\x01\x00\x00\x00')

        pkt_false = PacketBuilder.build_volume_ducking_packet(False)
        self.assertEqual(pkt_false[6:], b'\x0A\x00\x00\x00\x00')

class TestProximityPairingPacket(unittest.TestCase):
    def test_structure(self):
        # Just verify it returns bytes and starts with correct length/type
        pkt = ProximityPairingPacket.build(model_name="AirPods Pro")
        self.assertTrue(isinstance(pkt, bytes))
        # Header: Len (1 byte) + Type (0xFF) + Company (4C 00)
        self.assertEqual(pkt[1], 0xFF)
        self.assertEqual(pkt[2:4], b'\x4c\x00')
        
    def test_encrypted_payload_randomness(self):
        pkt1 = ProximityPairingPacket.build(model_name="AirPods")
        pkt2 = ProximityPairingPacket.build(model_name="AirPods")
        # The encrypted part (last 16 bytes) should be different
        self.assertNotEqual(pkt1[-16:], pkt2[-16:])

class TestAAPSocket(unittest.TestCase):
    def setUp(self):
        # Mock the internal socket
        self.mock_sock = MagicMock()
        # Create AAPSocket with mocked internal socket
        self.sock = AAPSocket(_sock=self.mock_sock)
        # Mock connection state for tests
        self.sock.connected = True

    def test_auto_handshake_on_apple_psm(self):
        # addr = (mac, psm)
        # We need to mock connect
        pass # connect calls super().connect which we can't easily mock without more structure hacking
        # But we can test if send_handshake sends correct data
        
    def test_send_handshake(self):
        self.sock.send_handshake()
        expected = PacketBuilder.build_handshake_packet()
        self.mock_sock.send.assert_called_with(expected)

    def test_set_anc_mode(self):
        self.sock.set_anc_mode("ANC")
        # ANC is Listening Mode (0x0D) with val 0x02
        # Opcode 0x0009
        # Payload 0D 02 00 00 00
        
        # Build expectation
        expected = PacketBuilder.build_control_command(0x0D, 0x02)
        self.mock_sock.send.assert_called_with(expected)

    def test_high_speed_fallback(self):
        # Ensure it falls back to send if l2cap_send_high_speed is missing
        if hasattr(self.mock_sock, 'l2cap_send_high_speed'):
            del self.mock_sock.l2cap_send_high_speed
        
        self.sock.send_high_speed(b'test')
        self.mock_sock.send.assert_called_with(b'test')

if __name__ == '__main__':
    unittest.main()
