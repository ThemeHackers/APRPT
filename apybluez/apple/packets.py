import struct

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
    OP_VIRTUAL_DEVICE_CONFIG = 0x0054

    CMD_MIC_MODE = 0x01
    CMD_CONVERSATIONAL_AWARENESS = 0x0A
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

    @staticmethod
    def build_volume_ducking_packet(enable: bool = True) -> bytes:
        val = 0x01 if enable else 0x00
        return PacketBuilder.build_control_command(PacketBuilder.CMD_CONVERSATIONAL_AWARENESS, val)

    @staticmethod
    def build_audiogram_payload(boost_high_freq: bool = True) -> bytes:
        if boost_high_freq:
            msg = bytes.fromhex("010200FFFFFF7F") 
        else:
            msg = bytes.fromhex("01020000000000")
            
        return PacketBuilder.build_packet(PacketBuilder.OP_HEADPHONE_ACCOMODATION, msg)
