import struct
import socket
import bluetooth._bluetooth as bluez

OGF_LE_CTL = 0x08
OCF_LE_SET_RANDOM_ADDRESS = 0x0005
OCF_LE_SET_ADVERTISING_PARAMETERS = 0x0006
OCF_LE_SET_ADVERTISE_ENABLE = 0x000A
OCF_LE_SET_ADVERTISING_DATA = 0x0008
ADV_NONCONN_IND = 0x03
ADV_IND = 0x00 # Connectable advertising

def set_random_le_address(sock, addr_bytes):
    # addr_bytes must be 6 bytes (reversed, little endian)
    cmd_pkt = struct.pack("<6B", *addr_bytes)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_RANDOM_ADDRESS, cmd_pkt)

def start_le_advertising(sock, min_interval=200, max_interval=200, adv_type=ADV_NONCONN_IND, data=(), own_bdaddr_type=0x00):
    # own_bdaddr_type: 0x00 for Public, 0x01 for Random
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

def open_dev(dev_id=0):
    try:
        return bluez.hci_open_dev(dev_id)
    except Exception as e:
        print(f"[!] Failed to open Bluetooth device hci{dev_id}: {e}")
        return None
