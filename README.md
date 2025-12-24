# Apple Protocol Research & Pentest Tool (APRPT)

**APRPT** is a proof-of-concept research tool designed to analyze and interact with the Apple Accessory Protocol (AAP) over Bluetooth Low Energy (BLE).

## 🚀 Concept & Philosophy

This project bridges the gap between passive spoofing and active protocol interaction by combining two core concepts found in `R&D/AppleBLE` and `R&D/librepods`:

1.  **Advertising & Spoofing**: Mimicking Apple devices to trigger UI events (Popups).
2.  **Active Protocol Control**: Establishing L2CAP connections to interact with internal device logic (AAP).

## 🔬 Mode Technical Breakdown

Here is the detailed technical explanation for every mode available in the tool:

### 1. Advertise Mode (`-m advertise`)
**Function**: Broadcasts fake "Proximity Pairing" signals.
**Goal**: To verify hardware transmission capabilities and demonstrate the "Phantom Device" effect.

*   **Mechanism**: Uses the HCI interface to send BLE Advertisement packets.
*   **Packet Structure**:
    *   **Length**: `0x1E` (30 bytes)
    *   **Type**: `0xFF` (Manufacturer Specific Data)
    *   **Company ID**: `0x004C` (Apple Inc.)
    *   **Beacon Type**: `0x07` (AirPods), `0x05`, `0x10`, etc.
*   **Effect**: iOS devices scanning in the background receive these packets and trigger the setup animation (the white bottom sheet popup), assuming a device is nearby.

### 2. Recon Mode (`-m recon`)
**Function**: Extracts device information not typically visible in standard BLE scans.
**Goal**: To identify firmware version, serial number, and battery status.

*   **Mechanism**: Connects via L2CAP PSM `0x1001` (Apple Accessory Protocol).
*   **Workflow**:
    1.  **Handshake**: Sends a specific byte sequence to initialize the AAP session.
    2.  **Subscription**: Sends Opcode `0x000F` (Subscribe Notifications) to listen for updates.
    3.  **Metadata Request**: Sends Opcode `0x1D` (Get Metadata).
*   **Payload**: The response to `0x1D` contains a TLV (Type-Length-Value) structure with details like the Serial Number, Model string, and current Firmware Revision.

### 3. Hijack Mode (`-m hijack`)
**Function**: Attempts to force the target device to switch its active audio source.
**Goal**: To demonstrate "Seamless Switching" vulnerabilities.

*   **Mechanism**: Sends high-priority Control Commands over the established L2CAP link.
*   **Key Opcodes**:
    *   **Opcode**: `0x09` (Control Command)
    *   **Payload `0x0601` (Owns Connection)**: Asserts urgency / ownership of the link.
    *   **Payload `0x2001` (Auto Connect)**: Instructs the device to trigger an auto-connection routine to the attacker's MAC address.
*   **Effect**: If successful, the AirPods disconnect from the current iPhone/Mac and connect to the Linux machine running this script.

### 4. Multi-Device Spoofing (NEW)
**Function**: Mimic various Apple devices.
**Goal**: To display different popups (AirPods Pro, Max, Apple TV, etc.) on the victim's screen.

*   **Usage**:
    *   Interactive: Run `sudo python3 main.py -m advertise` and select from the menu.
    *   Direct: Run `sudo python3 main.py -m advertise -M "AirPods Pro"`
*   **Mechanism**: Changes the **Product ID** sequence in the BLE advertisement payload to match specific Apple devices.

### 5. DoS Mode (`-m dos`)
**Function**: Stress tests the AAP implementation.
**Goal**: To cause a denial of service or instability in the target device's Bluetooth stack.

*   **Mechanism**: Continuously sends malformed or excessive AAP commands over an established L2CAP link.
*   **Key Opcodes**:
    *   **Opcode**: `0x09` (Control Command) with invalid payloads.
    *   **Opcode**: Rapid-fire `0x000F` (Subscribe Notifications) and `0x0010` (Unsubscribe Notifications).
*   **Effect**: Can lead to device crashes, temporary unresponsiveness, or forced disconnections.

### 6. HoneyPot Mode (`-m honeypot`)
**Function**: Traps victim devices that attempt to connect.
**Goal**: To detect which specific devices are responding to the spoofed signals.

*   **Mechanism**:
    *   Switches Advertising Type from `ADV_NONCONN_IND` (Broadcast Only) to `ADV_IND` (Connectable).
    *   Listens on the HCI socket for the `EVT_LE_CONN_COMPLETE` (0x3E) event.
*   **Effect**:
    *   The victim sees the popup and taps "Connect".
    *   The iOS device initiates a Link Layer connection request.
    *   The tool intercepts this request, extracts the **Mac Address** and **Connection Handle**, and alerts the attacker.
    *   It effectively deanonymizes the user who fell for the spoof.

## 📋 Requirements

*   **Operating System**: Linux (Required for raw L2CAP socket support via `bluez`).
*   **Hardware**: Bluetooth 4.0+ Adapter (Verified with Ugreen BLE 5.3).
*   **Dependencies**: python3, pybluez
*   **Root Privileges**: Required to access raw HCI sockets (`sudo` or `setcap`).

## 📦 Installation

Please follow these instructions exactly to avoid issues with Bluetooth dependencies (specifically `pybluez`).

### 1. Install System Dependencies
```bash
sudo apt update && sudo apt install -y bluez libpcap-dev libev-dev libnl-3-dev libnl-genl-3-dev libnl-route-3-dev cmake libbluetooth-dev
```

### 2. Install Python Dependencies
**Important:** Do not simply run `pip install pybluez`. The version on PyPI is broken.

```bash
# Install pybluez from source
pip3 install git+https://github.com/pybluez/pybluez.git#egg=pybluez

# Install other requirements
pip3 install pycryptodome
```
*(Note: Ensure your Bluetooth adapter is recognized as `hci0` using `hcitool dev`)*

## 💻 Usage

Run the tool using `python3 main.py`. Ensure you run with `sudo`.

```bash
# 1. Advertise (Spoofing) with Menu
sudo python3 main.py -m advertise

# 2. Advertise Specific Model
sudo python3 main.py -m advertise -M "AirPods Max"

# 3. Recon (Information Gathering)
sudo python3 main.py -t <TARGET_MAC> -m recon

# 4. Hijack (Active Attack)
sudo python3 main.py -t <TARGET_MAC> -m hijack

# 5. DoS (Stress Test)
sudo python3 main.py -t <TARGET_MAC> -m dos

# 5. HoneyPot (Victim Detection)
sudo python3 main.py -m honeypot
```

## ⚠️ Disclaimer

This tool is for **Educational and Research Purposes Only**.
The authors are not responsible for any misuse. Do not use this tool on devices you do not own or have explicit permission to test.
