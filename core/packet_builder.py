import struct
import random

class PacketBuilder:
    HEADER = b'\x04\x00\x04\x00'
    HANDSHAKE_PACKET = bytes.fromhex("00000400010002000000000000000000")
    
    OP_BATTERY = 0x0004
    OP_EAR_DETECTION = 0x0006
    OP_CONTROL_COMMAND = 0x0009
    OP_SUBSCRIBE_NOTIFICATIONS = 0x000F
    OP_HEAD_TRACKING = 0x0017
    OP_RENAME = 0x001A
    OP_METADATA = 0x001D
    OP_FEATURE_ENABLE = 0x004D
    OP_HEADPHONE_ACCOMODATION = 0x0053

    CMD_MIC_MODE = 0x01
    CMD_OWNS_CONNECTION = 0x06
    CMD_LISTENING_MODE = 0x0D
    CMD_AUTO_CONNECT = 0x20

    @staticmethod
    def build_packet(opcode: int, data: bytes = b"") -> bytes:
        opcode_bytes = struct.pack('<H', opcode)
        return PacketBuilder.HEADER + opcode_bytes + data

    @staticmethod
    def build_control_command(identifier: int, *args) -> bytes:
        payload = bytearray([identifier])
        for arg in args:
             payload.append(arg)
        
        while len(payload) < 5:
            payload.append(0x00)
            
        return PacketBuilder.build_packet(PacketBuilder.OP_CONTROL_COMMAND, bytes(payload))

    @staticmethod
    def build_handshake_packet() -> bytes:
        return PacketBuilder.HANDSHAKE_PACKET

    @staticmethod
    def build_subscription_packet() -> bytes:
        subscription_mask = bytes.fromhex("FFFFFEFF")
        return PacketBuilder.build_packet(PacketBuilder.OP_SUBSCRIBE_NOTIFICATIONS, subscription_mask)

    @staticmethod
    def build_metadata_request_packet() -> bytes:
        return PacketBuilder.build_packet(PacketBuilder.OP_METADATA)

class ProximityPairingPacket:
    MODELS = {
        "AirPods": (0x02, 0x20),
        "AirPods Pro": (0x0E, 0x20),
        "AirPods Max": (0x0A, 0x20),
        "AirPods Gen 2": (0x0F, 0x20),
        "AirPods Gen 3": (0x13, 0x20),
        "AirPods Pro Gen 2": (0x14, 0x20),
        "PowerBeats": (0x03, 0x20),
        "PowerBeats Pro": (0x0B, 0x20),
        "Beats Solo Pro": (0x0C, 0x20),
        "Beats Studio Buds": (0x11, 0x20),
        "Beats Flex": (0x10, 0x20),
        "BeatsX": (0x05, 0x20),
        "Beats Solo3": (0x06, 0x20),
        "Beats Studio3": (0x09, 0x20),
        "Beats Studio Pro": (0x17, 0x20),
        "Beats Fit Pro": (0x12, 0x20),
        "Beats Studio Buds+": (0x16, 0x20),
    }

    @staticmethod
    def build(model_name="AirPods", 
              battery_left=100, battery_right=100, battery_case=100, 
              charging_left=False, charging_right=False, charging_case=False,
              lid_open=True, color=0x00, subtype=0x07):
        
        prefix = bytes([subtype, 0x19])
        pairing_mode = b'\x01'
        model_bytes = bytes(ProximityPairingPacket.MODELS.get(model_name, (0x02, 0x20)))
        status = b'\x20' 
        
        def enc_bat(val):
            if val >= 100: return 0xA
            if val < 0: return 0xF
            return int(val / 10)
            
        bat_left = enc_bat(battery_left)
        bat_right = enc_bat(battery_right)
        battery_byte = bytes([(bat_left << 4) | bat_right])
        
        bat_case = enc_bat(battery_case)
        flags = 0
        if charging_right: flags |= 1
        if charging_left: flags |= 2
        if charging_case: flags |= 4
        
        flags_case_byte = bytes([(bat_case << 4) | flags])
        lid_byte = b'\x01' if lid_open else b'\x09'
        color_byte = bytes([color])
        
        encrypted_payload = bytes([random.randint(0, 255) for _ in range(16)])
        padding = b'\x00'
        
        raw_payload = prefix + pairing_mode + model_bytes + status + battery_byte + flags_case_byte + lid_byte + color_byte + padding + encrypted_payload
        
        apple_id = b'\x4c\x00'
        header = bytes([len(apple_id) + len(raw_payload) + 1, 0xFF])
        
        return header + apple_id + raw_payload
