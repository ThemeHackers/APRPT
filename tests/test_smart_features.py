import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.packet_builder import PacketBuilder
from modules.hijack import HijackModule
from modules.context_aware import ContextAttackModule
from core.connection import AAPConnection

class TestSmartFeatures(unittest.TestCase):

    def setUp(self):
        self.mock_conn = MagicMock(spec=AAPConnection)
        self.mock_conn.sock = True 
        self.mock_console = MagicMock()
        self.hijack = HijackModule(self.mock_conn, self.mock_console)
        self.context = ContextAttackModule(self.mock_console)
        self.context.rssi_threshold = -60

    def test_ducking_packet_structure(self):
        pkt = PacketBuilder.build_volume_ducking_packet(enable=True)
        
        self.assertEqual(pkt[4], 0x09) 
        self.assertEqual(pkt[5], 0x00)
        self.assertEqual(pkt[6], 0x0A) 
        self.assertEqual(pkt[7], 0x01) 

    def test_audiogram_packet_structure(self):
        pkt = PacketBuilder.build_audiogram_payload(boost_high_freq=True)
        self.assertEqual(pkt[4], 0x53)
        self.assertEqual(pkt[5], 0x00)

    @patch('time.sleep', return_value=None) 
    @patch('time.time')
    def test_ghost_ducking_randomization(self, mock_time, mock_sleep):
        mock_time.side_effect = [0, 1, 2, 3, 11] 
        
        with patch('random.uniform') as mock_random:
            mock_random.return_value = 1.23 
            
            self.hijack.trigger_volume_ducking(duration_sec=10, ghost_mode=True)
            
            self.assertTrue(self.mock_conn.send.called)
            
            self.assertTrue(mock_random.called)
            mock_sleep.assert_any_call(1.23)

    @patch('time.sleep', return_value=None)
    def test_boiling_frog_calls(self, mock_sleep):
        self.hijack.write_malicious_audiogram(boiling_frog=True)
        
        self.assertEqual(self.mock_conn.send.call_count, 5)
        mock_sleep.assert_any_call(1.5)

    def test_smart_debounce_ignore_transient(self):
        mac = "00:11:22:33:44:55"
        
        self.context._zone_callback(mac, -50, {}, smart=True)
        self.assertEqual(len(self.context.rssi_history[mac]), 1)
        
        self.mock_console.print.reset_mock()
        
        self.context._zone_callback(mac, -50, {}, smart=True)
        self.mock_console.print.assert_not_called()
        
        self.context._zone_callback(mac, -90, {}, smart=True)
        
        self.context._zone_callback(mac, -50, {}, smart=True)
    
    def test_smart_debounce_trigger_stable(self):
        mac = "AA:BB:CC:DD:EE:FF"
        
        self.context._zone_callback(mac, -40, {}, smart=True)
        self.context._zone_callback(mac, -40, {}, smart=True)
        self.context._zone_callback(mac, -40, {}, smart=True)
        
        found = False
        for call in self.mock_console.print.call_args_list:
            if "PROXIMITY ALERT" in str(call):
                found = True
                break
        self.assertTrue(found, "Smart Debounce should have triggered on stable signal")

if __name__ == '__main__':
    unittest.main()
