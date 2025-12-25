# 🍎 **APRPT** (Apple Protocol Research & Pentest Tool)

> **"Bridging the gap between Passive Spoofing & Active Manipulation"**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux-red?style=for-the-badge&logo=linux)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-PoC-yellow?style=for-the-badge)

**APRPT** is a powerful research framework designed to analyze, interact with, and stress-test the **Apple Accessory Protocol (AAP)** over Bluetooth Low Energy (BLE). It unifies "Ghost" techniques (Spoofing) with "Aggressor" techniques (Active L2CAP Control).

---

## 🚀 **Concept & Philosophy**

This project fuses two distinct research philosophies into one offensive toolkit:

1.  🎭 **The Phantom (Advertising & Spoofing)**: Mimicking Apple devices to trigger UI popups and "phantom" presence. (Derived from `AppleBLE`)
2.  ⚔️ **The Aggressor (Active Protocol Control)**: Establishing raw **L2CAP** connections to hijack device state. (Derived from `LibrePods`)

> **Integration Matrix**: APRPT mixes these strands—using "Phantom" logic for Phishing and "Aggressor" logic for Weaponization (e.g., forcing audio switching).

---

## 🛠️ **Features & Modes**

| Mode | Flag | Functionality |
| :--- | :--- | :--- |
| **Advertiser** | `-m advertise` | 📡 **Phishing / Spoofing**: Broadcasts fake "Proximity Pairing" signals. Supports **Phishing Mode** (Cycle Models). |
| **Passive Sniffer** | `-m sniff` | 🕵️ **Surveillance**: Decodes nearby advertisements. Supports **Targeted Pattern of Life** logging & **Spoof Detection**. |
| **Reconnaissance** | `-m recon` | 🔍 **Intel**: Connects & extracts Serial Numbers, Firmware, and **Scans for known CVEs**. |
| **Hijack** | `-m hijack` | 🔀 **Control**: Forces target AirPods to switch audio routing to the attacker's machine. |
| **Active Control** | `-m control` | 🎮 **Manipulation**: **Rename Devices**, **Strobe ANC**, or monitor **Head Tracking** via L2CAP. |
| **DoS** | `-m dos` | ⛔ **Availability**: Performs **L2CAP Resource Exhaustion** or Packet Flooding. |
| **BLE Fuzzer** | `-m bleed` | 🩸 **Stress Test**: Supports Area Bleed or **Targeted Protocol Fuzzing**. |
| **HoneyPot** | `-m honeypot` | 🕸️ **Trap**: Detects and logs MAC addresses of victims attempting to connect to spoofed signals. |
| **PCAP Analysis** | `-m analyze` | 🧠 **Forensics**: Deep inspection of key packets (HCI/AAP) & Proximity Pairing decoding. |
| **Context Aware** | `-m context` | 📍 **Automation**: Triggers attacks based on environmental triggers like RSSI zones or activity state. |

---

## 🔬 **Technical Deep Dive & New Features**

### 1. **Advanced Reconnaissance** (`-m sniff` / `-m recon`)
*   **Targeted Tracking**: Filters traffic for a specific MAC and logs RSSI/Status history to CSV for Pattern of Life analysis.
*   **Spoof Detection**: Identifies devices broadcasting "Pairing Mode" flags suspiciously, indicating a potential ongoing spoofing attack.
*   **Firmware Scanner**: Automatically checks extracted firmware versions against a local database of mock vulnerabilities (CVEs).

### 2. **Social Engineering** (`-m advertise` / `-m control`)
*   **Phishing Mode**: Rapidly cycles through all device models to flood nearby users with "Not Your AirPods" popups.
*   **Device Renaming**: Uses L2CAP Opcode `0x1A` to permanently rename a target device (e.g., "Connection Failed"), a persistent deception attack.

### 3. **Availability & DoS** (`-m dos` / `-m bleed`)
*   **L2CAP Flood**: Exhausts the target's connection handles by opening maximal parallel L2CAP sockets.
*   **Protocol Fuzzing**: Targets PSM `0x1001` with randomized AAP headers and payloads to trigger stack crashes.

### 4. **Side-Channel Analysis** (`-m control`)
*   **Head Tracking Monitor**: Intercepts Opcode `0x17` packets to real-time monitor the user's head movement (Privacy Leak).

### 5. **Active Control** (`-m control`)
*   **Strobe Mode**: Rapidly toggles between ANC and Transparency to clinically disorient the user (Acoustic Attack).

### 6. **Deep Feature Hijacking** (`-m hijack`)
*   **Malicious Audiogram**: Injects a custom audio profile (Opcode `0x53`) to boost high frequencies, turning Transparency Mode into an acoustic weapon.
*   **Volume Ducking**: Abuses "Conversation Awareness" to silence media playback remotely.
*   **Handover Jamming**: Exploits the Magic Switch feature to aggressively force a handover to the attacker.

### 7. **Context-Aware Modules** (`-m context`)
*   **Zone Denial**: Automatically attacks any device entering a defined RSSI perimeter ("Digital Landmine").
*   **Activity Trigger**: Lies in wait (Passive Sniff) until a victim puts headphones in (In-Ear Detection) to launch an attack.

### 8. **Smart Enhancements** (`--smart`)
*   **Ghost Mode**: Randomizes attack patterns (e.g., volume glitches) to mimic hardware failure.
*   **Boiling Frog**: Gradually ramps up attack intensity (e.g., audiogram gain) to avoid immediate detection.
*   **Adaptive Jamming**: Varies packet timing to evade simple spam filters.

---

## 📦 **Installation**

> ⚠️ **Prerequisites**: Linux OS with a Bluetooth 4.0+ Adapter.

### 1. System Dependencies
```bash
sudo apt update && sudo apt install -y bluez libpcap-dev libev-dev libnl-3-dev libnl-genl-3-dev libnl-route-3-dev cmake libbluetooth-dev
```

### 2. Python Setup
**CRITICAL**: Do NOT install `pybluez` via pip directly. Use the source:
```bash
# Install PyBluez from source (Fixed for Python 3)
pip3 install git+https://github.com/pybluez/pybluez.git#egg=pybluez

# Install crypto libs
pip3 install pycryptodome rich scapy
```

---

## 💻 **Usage Guide**

**Note**: All commands require **ROOT** privileges (`sudo`) for raw socket access.

### 📡 Social Engineering
```bash
# Phishing Mode (Cycle detailed models)
sudo python3 main.py -m advertise --phishing

# Rename Device (Persistent)
sudo python3 main.py -m control -t <TARGET_MAC>
# Select Option 4 in the menu
```
> **Physical Result**:
> *   **Phishing**: Victim receives a barrage of "Not Your AirPods" popups.
> *   **Rename**: Target device name changes in Bluetooth settings to "Connection Failed".

### 🕵️ Advanced Recon
```bash
# Pattern of Life Logging
sudo python3 main.py -m sniff -t <TARGET_MAC> --log-file target.csv

# Vulnerability Scan
sudo python3 main.py -m recon -t <TARGET_MAC>
```
> **Physical Result**:
> *   **Sniffer**: `pol.csv` created with specific RSSI/Status history.
> *   **Recon**: Console alerts on "VULNERABILITY DETECTED" if firmware matches known CVEs.

### 🔎 Forensics & Analysis
```bash
# Analyze a PCAPNG file (with Proximity Pairing decoding)
sudo python3 main.py -m analyze -f <file.pcapng> -v

# View Known Opcode Definitions
sudo python3 main.py --definitions
```

### 🎮 Side-Channel & Active Control
```bash
sudo python3 main.py -m control -t <TARGET_MAC>
# Options:
# 5. Head Tracking Monitor
# 6. Strobe Mode (Disorient)
```
> **Physical Result**:
> *   **Strobe**: Victim hears rapid switching between Silence (ANC) and Noise (Transparency).
> *   **Head Tracking**: Console logs real-time XYZ coordinates of the user's head.

### 🩸 Availability / DoS
```bash
# L2CAP Resource Exhaustion
sudo python3 main.py -m dos -t <TARGET_MAC>

# Targeted Protocol Fuzzing
sudo python3 main.py -m bleed -t <TARGET_MAC>
```
> **Physical Result**:
> *   **DoS**: Target device cannot connect to iPhone; user sees "Connection Failed".
> *   **Bleed**: Target headphones may reboot, disconnect, or stop audio.

### 🕸️ Victim Trap (HoneyPot)
```bash
sudo python3 main.py -m honeypot
```
> **Physical Result**:
> *   **Victim**: iPhone gets stuck on **"Hold Button"** screen.
> *   **Attacker**: Successfully logs the victim's MAC address.

---

## 🚧 **System Limitations**

1.  **The "Hold Button" Barrier**: When using HoneyPot, the victim's iPhone will get stuck on the "Hold Button" screen. We cannot proceed to "Pairing Success" because generic Bluetooth dongles lack the proprietary Apple W1/H1 chips required for the cryptographic handshake.
2.  **Single Adapter Blindness**: You cannot sniff your own packets. If running `-m advertise` and `-m sniff` on the same machine with one adapter (`hci0`), the sniffer will show nothing. Use a second device to test.
3.  **Zero-Trust Access**: We can hijack audio *routing* (force them to hear us), but we cannot hear *their* microphone or access their iCloud settings due to missing Link Keys.

---

## ⚠️ **Disclaimer & Ethics**

> 🛑 **EDUCATIONAL USE ONLY**
>
> This tool involves **Active Interception** and **Protocol Manipulation**. It is intended for researchers to demonstrate Bluetooth risks.
> *   Do not use on devices you do not own.
> *   Do not use in public spaces to harass others.
> *   The authors are not responsible for bricked devices or legal consequences.

---

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-blue" />
  <img src="https://img.shields.io/badge/Security-Research-red" />
</p>
