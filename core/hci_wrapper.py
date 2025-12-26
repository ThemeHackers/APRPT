import struct
import socket
import bluetooth._bluetooth as bluez

OGF_LE_CTL = 0x08
OCF_LE_SET_RANDOM_ADDRESS = 0x0005
OCF_LE_SET_ADVERTISING_PARAMETERS = 0x0006
OCF_LE_SET_ADVERTISE_ENABLE = 0x000A
OCF_LE_SET_ADVERTISING_DATA = 0x0008
ADV_NONCONN_IND = 0x03
ADV_IND = 0x00

OGF_LINK_CTL = 0x01
OCF_DISCONNECT = 0x0006

def set_random_le_address(sock, addr_bytes):
    cmd_pkt = struct.pack("<6B", *addr_bytes)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_RANDOM_ADDRESS, cmd_pkt)

def start_le_advertising(sock, min_interval=200, max_interval=200, adv_type=ADV_NONCONN_IND, data=(), own_bdaddr_type=0x00):
    cmd_pkt = struct.pack("<HHBBB6BBB", min_interval, max_interval, adv_type, own_bdaddr_type, 0, 0, 0, 0, 0, 0, 0, 0x07, 0)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_PARAMETERS, cmd_pkt)

    cmd_pkt = struct.pack("<B", 0x01)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISE_ENABLE, cmd_pkt)

    data_length = len(data)
    if data_length > 31:
        data = data[:31]
        data_length = 31
        
    cmd_pkt = struct.pack("<B%dB" % data_length, data_length, *data)

def set_random_le_address(sock, addr_bytes):
    cmd_pkt = struct.pack("<6B", *addr_bytes)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_RANDOM_ADDRESS, cmd_pkt)

def start_le_advertising(sock, min_interval=200, max_interval=200, adv_type=ADV_NONCONN_IND, data=(), own_bdaddr_type=0x00):
    cmd_pkt = struct.pack("<HHBBB6BBB", min_interval, max_interval, adv_type, own_bdaddr_type, 0, 0, 0, 0, 0, 0, 0, 0x07, 0)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_PARAMETERS, cmd_pkt)

    cmd_pkt = struct.pack("<B", 0x01)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISE_ENABLE, cmd_pkt)

    data_length = len(data)
    if data_length > 31:
        data = data[:31]
        data_length = 31
        
    cmd_pkt = struct.pack("<B%dB" % data_length, data_length, *data)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_DATA, cmd_pkt)

def stop_le_advertising(sock):
    cmd_pkt = struct.pack("<B", 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISE_ENABLE, cmd_pkt)

OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C

def enable_le_scan(sock, enabled=True, filter_duplicates=False):
    enable_flag = 0x01 if enabled else 0x00
    dup_flag = 0x01 if filter_duplicates else 0x00
    
    scan_params = struct.pack("<BHHBB", 0x01, 0x0010, 0x0010, 0x00, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_PARAMETERS, scan_params)
    
    cmd_pkt = struct.pack("<BB", enable_flag, dup_flag)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

def open_dev(dev_id=0):
    try:
        return bluez.hci_open_dev(dev_id)
    except Exception as e:
        print(f"[!] Failed to open Bluetooth device hci{dev_id}: {e}")
        return None

def disconnect_handle(sock, handle, reason=0x13):
    cmd_pkt = struct.pack("<HB", handle, reason)
    bluez.hci_send_cmd(sock, OGF_LINK_CTL, OCF_DISCONNECT, cmd_pkt)