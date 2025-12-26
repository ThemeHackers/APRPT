import unittest
from unittest.mock import MagicMock, patch
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apybluez.apple.socket import AAPSocket
from apybluez.hci.wrapper import start_spoof
from apybluez.exceptions import AAPCommandError, AAPConnectionError, HCISpoofingError
import apybluez.bluetooth as bluetooth

class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.mock_sock = MagicMock()
        self.sock = AAPSocket(_sock=self.mock_sock)

    def test_invalid_anc_mode(self):
        with self.assertRaises(AAPCommandError):
            self.sock.set_anc_mode("InvalidMode")

    def test_send_not_connected(self):
        self.sock.connected = False
        with self.assertRaises(AAPConnectionError):
            self.sock.send(b'test')

    def test_connect_failure(self):
        with patch('apybluez.apple.socket.bluetooth.BluetoothSocket.connect') as mock_super_connect:
            mock_super_connect.side_effect = bluetooth.BluetoothError("Connection refused")
            with self.assertRaises(AAPConnectionError):
                self.sock.connect(("00:00:00:00:00:00", 0x1001))
            self.assertFalse(self.sock.connected)

    def test_spoof_device_open_failure(self):
        with patch('apybluez.bluetooth._bluetooth.hci_open_dev') as mock_open:
            mock_open.side_effect = Exception("Device busy")
            with self.assertRaises(HCISpoofingError):
                start_spoof(device_id=99)

if __name__ == '__main__':
    unittest.main()
