import random

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
    def build_legacy_honeypot_packet(left, right, case):
        prefix = bytes([0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x01, 0x02, 0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45])
        suffix = bytes([0xda, 0x29, 0x58, 0xab, 0x8d, 0x29, 0x40, 0x3d, 0x5c, 0x1b, 0x93, 0x3a])
        return prefix + bytes([left, right, case]) + suffix

    @staticmethod
    def build(model_name="AirPods", 
              battery_left=100, battery_right=100, battery_case=100, 
              charging_left=False, charging_right=False, charging_case=False,
              lid_open=True, color=0x00, subtype=0x07):
        
        # Fixed Prefix for "Not Your AirPods" popup trigger
        # 1 byte: SubType (0x07)
        # 1 byte: Length (0x19 = 25 bytes)
        # 1 byte: Pairing Mode (0x07 = R&D Reference / General Compatibility)
        prefix = bytes([subtype, 0x19, 0x07])
        
        model_bytes = bytes(ProximityPairingPacket.MODELS.get(model_name, (0x02, 0x20)))
        # Status 0x75 is critical for "Not Your AirPods" popup on iOS 17+ 
        status = b'\x75' 
        
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
        
       
        raw_payload = prefix + model_bytes + status + battery_byte + flags_case_byte + lid_byte + color_byte + padding + encrypted_payload
        
        apple_id = b'\x4c\x00'
        
        packet_len = len(apple_id) + len(raw_payload) + 1
        header = bytes([packet_len, 0xFF])
        
        return header + apple_id + raw_payload
