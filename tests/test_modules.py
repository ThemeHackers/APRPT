import unittest
from unittest.mock import MagicMock, patch
import sys

sys.modules['bluetooth'] = MagicMock()
sys.modules['bluetooth._bluetooth'] = MagicMock()

from core.connection import AAPConnection
from modules.recon import ReconModule
from modules.hijack import HijackModule
from core.packet_builder import PacketBuilder

class TestModules(unittest.TestCase):

    def setUp(self):
        self.mock_conn = MagicMock(spec=AAPConnection)
        self.mock_conn.sock = MagicMock() # Simulate connected
        self.mock_conn.send.return_value = True

    def test_recon_flow(self):
        module = ReconModule(self.mock_conn)
        
        self.mock_conn.receive.side_effect = [
            b'\x00\x00', # Handshake ack
            b'\x00\x00', # Sub ack
            b'...Name:AirPods...' # Metadata
        ]
        
        module.get_device_info()
        
        self.assertEqual(self.mock_conn.send.call_count, 3)
        
        args, _ = self.mock_conn.send.call_args_list[2]
        sent_pkt = args[0]
        self.assertEqual(sent_pkt[4:6], b'\x1D\x00')

    def test_hijack_flow(self):
        module = HijackModule(self.mock_conn)
        
        self.mock_conn.receive.return_value = b'\x00'
        
        module.run_smart_routing_hijack()
        
        self.assertEqual(self.mock_conn.send.call_count, 2)
        
        args1, _ = self.mock_conn.send.call_args_list[0]
        pkt1 = args1[0]
        self.assertEqual(pkt1[4:6], b'\x09\x00') # Opcode 9
        self.assertEqual(pkt1[6], 0x06)          # Identifier 0x06

        args2, _ = self.mock_conn.send.call_args_list[1]
        pkt2 = args2[0]
        self.assertEqual(pkt2[6], 0x20)          # Identifier 0x20

if __name__ == '__main__':
    unittest.main()
