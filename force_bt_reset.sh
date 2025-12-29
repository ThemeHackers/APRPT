#!/bin/bash
echo "Starting aggressive Bluetooth reset..."


echo "[*] Stopping Bluetooth service..."
service bluetooth stop


echo "[*] Unblocking all RF devices..."
rfkill unblock all


echo "[*] Removing Bluetooth kernel modules..."
modprobe -r btusb
modprobe -r bnep
modprobe -r bluetooth

sleep 2

echo "[*] Reloading Bluetooth kernel modules..."
modprobe bluetooth
modprobe btusb


echo "[*] Starting Bluetooth service..."
service bluetooth start

sleep 2

echo "[*] Resetting hci0 interface..."
hciconfig hci0 reset
hciconfig hci0 up

echo "[*] Current Status:"
hciconfig -a

echo "Done."
