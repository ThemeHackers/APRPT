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

---

## 🛠️ **Features & Modes**

| Mode | Flag | Functionality |
| :--- | :--- | :--- |
| **Advertiser** | `-m advertise` | 📡 **Spoofing**: Broadcasts fake "Proximity Pairing" signals to trigger popups on nearby iOS devices. |
| **Passive Sniffer** | `-m sniff` | 🕵️ **Surveillance**: Decodes nearby Apple advertisements (Battery, Model, Lid Status) *without connecting*. |
| **Reconnaissance** | `-m recon` | 🔍 **Intel**: Connects & extracts Serial Numbers, Firmware Versions via standard AAP. |
| **Hijack** | `-m hijack` | 🔀 **Control**: Forces target AirPods to switch audio routing to the attacker's machine. |
| **Active Control** | `-m control` | 🎮 **Manipulation**: Toggles **ANC / Transparency** modes or renames devices via L2CAP. |
| **DoS** | `-m dos` | ⛔ **Denial of Service**: Floods standard AAP commands to crash the firmware. |
| **BLE Fuzzer** | `-m bleed` | 🩸 **Stress Test**: Floods the environment with malformed/oversized packets. |
| **HoneyPot** | `-m honeypot` | 🕸️ **Trap**: Detects and logs MAC addresses of victims attempting to connect to spoofed signals. |

---

## 🔬 **Technical Deep Dive**

### 1. **Advertise Mode** (`-m advertise`)
*   **Mechanism**: Raw HCI commands to broadcast Manufacturer Specific Data (`0x004C`).
*   **Payload**: Uses Beacon Type `0x07` (Proximity Pairing) to mimic AirPods.
*   **Effect**: Triggers the "Not Your AirPods" setup animation on iOS.

### 2. **Passive Sniffer** (`-m sniff`)
*   **Mechanism**: Promiscuous BLE scanning + Bitwise decoding of `0x07` payloads.
*   **Capabilities**:
    *   🔋 Battery Levels (L/R/Case)
    *   🎧 Device Model Identification
    *   🚨 **Spoof Detection**: Flags devices broadcasting "Pairing" bits suspiciously.

### 3. **Active Control** (`-m control`)
*   **Mechanism**: Connects to **L2CAP PSM 0x1001**.
*   **Attack**: Sends AAP `Opcode 0x09` (Control Command).
    *   *Force Transparency*: Disable ANC against user will.
    *   *Force ANC*: Isolate user from environment.

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
pip3 install pycryptodome rich
```

---

## 💻 **Usage Guide**

**Note**: All commands require **ROOT** privileges (`sudo`) for raw socket access.

### 📡 Spoofing (Visual Spam)
```bash
sudo python3 main.py -m advertise
# Or specific model:
sudo python3 main.py -m advertise -M "AirPods Max"
```

### 🕵️ Passive Surveillance
```bash
sudo python3 main.py -m sniff
```

### 🔍 Recon & Hijack (Legacy)
```bash
# Get Info targeting specific device
sudo python3 main.py -m recon -t <TARGET_MAC>

# Hijack Audio Routing
sudo python3 main.py -m hijack -t <TARGET_MAC>
```

### 🎮 Active Control (New Hijack)
```bash
sudo python3 main.py -m control -t <TARGET_MAC>
```

### 🩸 Fuzzing / DoS
```bash
# Protocol DoS (Targeted)
sudo python3 main.py -m dos -t <TARGET_MAC>

# BLE Fuzzer (Area Effect)
sudo python3 main.py -m bleed
```

### 🕸️ Victim Trap (HoneyPot)
```bash
sudo python3 main.py -m honeypot
```

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
