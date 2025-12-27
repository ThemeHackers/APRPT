import apybluez.bluetooth as bluetooth
from .packets import PacketBuilder
from ..exceptions import AAPConnectionError, AAPCommandError

class AAPSocket(bluetooth.BluetoothSocket):
    def __init__(self, proto=bluetooth.L2CAP, _sock=None):
        super().__init__(proto, _sock)
        self.connected = False

    def connect(self, addr):
        try:
            super().connect(addr)
            self.connected = True
            
            if isinstance(addr, tuple) and len(addr) >= 2 and addr[1] == 0x1001:
                self.send_handshake()
        except bluetooth.BluetoothError as e:
            self.connected = False
            raise AAPConnectionError(f"Failed to connect to {addr}: {e}")

    def _ensure_connected(self):
        if not self.connected:
            raise AAPConnectionError("Socket is not connected.")

    def send(self, data):
        self._ensure_connected()
        try:
            return super().send(data)
        except bluetooth.BluetoothError as e:
            self.connected = False
            raise AAPConnectionError(f"Failed to send data: {e}")

    def send_handshake(self):
        pkt = PacketBuilder.build_handshake_packet()
        self.send(pkt)

    def set_anc_mode(self, mode_name="ANC"):
        """
        Sets ANC mode: Off, ANC, Transparency, Adaptive
        """
        mode_map = {
            "Off": 0x01,
            "ANC": 0x02,
            "Transparency": 0x03,
            "Adaptive": 0x04
        }
        if mode_name not in mode_map:
            raise AAPCommandError(f"Invalid ANC mode: {mode_name}. Valid modes: {list(mode_map.keys())}")
            
        val = mode_map[mode_name]
        pkt = PacketBuilder.build_control_command(PacketBuilder.CMD_LISTENING_MODE, val)
        self.send(pkt)

    def set_conversational_awareness(self, state=True):
        pkt = PacketBuilder.build_volume_ducking_packet(state)
        self.send(pkt)

    def get_battery_status(self):
        self._ensure_connected()
        try:
            data = self.recv(1024)
            if len(data) >= 6:
                opcode = int.from_bytes(data[4:6], byteorder='little')
                if opcode == PacketBuilder.OP_BATTERY:
                    return data
            return None
        except bluetooth.BluetoothError as e:
            raise AAPConnectionError(f"Failed to receive battery status: {e}")

    def send_high_speed(self, data):
        """
        Uses the optimized C extension method l2cap_send_high_speed if available.
        Otherwise falls back to standard send.
        """
        self._ensure_connected()
        if hasattr(self._sock, "l2cap_send_high_speed"):
             try:
                 return self._sock.l2cap_send_high_speed(data)
             except Exception as e:
                 raise AAPConnectionError(f"High speed send failed: {e}")
        else:
             return self.send(data)
