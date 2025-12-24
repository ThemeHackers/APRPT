import unittest
import sys
import os
from unittest.mock import MagicMock


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.control import ControlModule

class TestControlLogic(unittest.TestCase):
    def setUp(self):
        self.control = ControlModule(console=None, target="00:00:00:00:00:00")
        self.control.sock = MagicMock()

    def test_send_handshake(self):
        """Test the exact bytes of the handshake."""
        self.control.send_handshake()
        
        expected_bytes = bytes.fromhex("00 00 04 00 01 00 02 00 00 00 00 00 00 00 00 00")
        self.control.sock.send.assert_called_with(expected_bytes)

    def test_set_noise_control_transparency(self):
        """Test Transparency command bytes (Mode 0x03)."""
        self.control.set_noise_control(0x03)
    
        expected_bytes = b'\x04\x00\x04\x00\x09\x00\x0D\x03\x00\x00\x00'
        
        self.control.sock.send.assert_called_with(expected_bytes)

    def test_set_noise_control_anc(self):
        """Test ANC command bytes (Mode 0x02)."""
        self.control.set_noise_control(0x02)
        expected_bytes = b'\x04\x00\x04\x00\x09\x00\x0D\x02\x00\x00\x00'
        self.control.sock.send.assert_called_with(expected_bytes)

if __name__ == '__main__':
    unittest.main()
