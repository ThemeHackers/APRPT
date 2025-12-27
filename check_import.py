import sys
import apybluez
import apybluez.apple.proximity

print(f"apybluez location: {apybluez.__file__}")
print(f"proximity location: {apybluez.apple.proximity.__file__}")

from apybluez.apple.proximity import ProximityPairingPacket
pkt = ProximityPairingPacket.build(model_name="AirPods Pro")
print(f"Packet[0]: {hex(pkt[0])}")
