# 📘 AAP Definitions & Reference
> *As per AirPods Pro 2 (USB-C) Firmware 7A305*

---

## 🏛️ **Protocol Overview**

**Apple Accessory Protocol (AAP)** is a proprietary application-layer protocol running over **Bluetooth Low Energy (BLE)** L2CAP. It enables rich feature control and real-time status monitoring for Apple audio accessories (AirPods, Beats).

### 📡 Architecture
AAP runs on top of **L2CAP** using **PSM `0x1001`**.

| Layer | Protocol | Description |
| :--- | :--- | :--- |
| **App** | **AAP** | Custom commands (Noise Control, Battery, Settings) |
| **Transport** | **L2CAP** | Packet segmentation on PSM `0x1001` |
| **Radio** | **BLE** | Physical layer |

### 📦 Packet Structure
All AAP packets follow a uniform structure:

```
[Header] [Opcode] [Data]
```

*   **Header**: `04 00 04 00` (Fixed Preamble)
*   **Opcode**: 2 Bytes (Little Endian)
*   **Data**: Variable length payload

---

## 🤝 **Connection Handshake**

To establish control, you **must** send this handshake immediately after connecting to L2CAP PSM `0x1001`.

**Handshake Packet:**
```python
# Hex: 00 00 04 00 01 00 02 00 ... (Zeros)
packet = bytes.fromhex("00000400010002000000000000000000")
```

> ⚠️ **Note**: Without this, the AirPods will silently ignore all subsequent commands.

---

## 🕹️ **Control Commands** (Writing)

### 1. Change Noise Control Mode
Controls ANC and Transparency.

**Opcode**: `0x0009`  
**Sub-Command**: `0x0D`

**Packet Format:**
```plaintext
04 00 04 00 09 00 0D [Mode] 00 00 00
```

| Mode Name | Byte Value | Description |
| :--- | :--- | :--- |
| **Off** | `0x01` | Passive isolation. |
| **ANC** | `0x02` | Active Noise Cancellation. |
| **Transparency** | `0x03` | Passthrough audio. |
| **Adaptive** | `0x04` | Dynamic adjustment (Requires Unlock). |

---

### 2. Conversational Awareness (Volume Ducking)
Triggers the "User Speaking" state to lower media volume.

**Opcode**: `0x0009` (Shared Control) or `0x000A` (Direct)
In this toolkit, we use the specific control command found in logs:
**Command ID**: `0x0A`

**Packet Format:**
```plaintext
04 00 04 00 09 00 0A [State] 00 00 00
```
**State**: `0x01` (Speaking), `0x00` (Silent)

---

### 3. Headphone Accommodation (Audiogram)
Writes custom transparency / equalizer settings.

**Opcode**: `0x0053`

**Packet Format:**
```plaintext
04 00 04 00 53 00 [Command] [SubCmd] [Payload...]
```
*   **Command**: `0x01` (Write)
*   **Payload**: CoreAudio binary structure (Gain, Freq, Q-Factor).

---

### 2. Rename Device
Sets the display name of the AirPods.

**Opcode**: `0x001A`

**Packet Format:**
```plaintext
04 00 04 00 1A 00 01 [Length] 00 [Name String]
```

---

### 3. Feature Unlock (Adaptive / Conversation)
Required to enable "Adaptive Transparency" and "Conversation Awareness" on non-Apple devices.

**Opcode**: `0x004D`

**Packet Format:**
```plaintext
04 00 04 00 4D 00 FF 00 00 00 00 00 00 00
```

---

## 🔔 **Notifications** (Reading)

To receive updates, you must subscribe first.

### 1. Subscribe to Notifications
**Opcode**: `0x000F`

**Packet Format:**
```plaintext
04 00 04 00 0F 00 FF FF FE FF
```

### 2. Battery Status Report
Received periodically or on change.

**Opcode**: `0x0004` (in response)

**Packet Analysis:**
```plaintext
Header(4) + Opcode(2) + Count(2) + [Component Blocks...]
```

**Component Block Structure:**
`[ID] 01 [Level] [Status] 01`

| Component | ID |
| :--- | :--- |
| **Right Pod** | `0x02` |
| **Left Pod** | `0x04` |
| **Case** | `0x08` |

---

## 🧭 **Head Tracking**

Stream real-time orientation data.

### Start Tracking
**Opcode**: `0x0017`

**Packet:**
```plaintext
04 00 04 00 17 00 00 00 10 00 10 00 08 A1 02 42 0B 08 0E 10 02 1A 05 01 40 9C 00 00
```

### Stop Tracking
**Packet:**
```plaintext
04 00 04 00 17 00 00 00 10 00 11 00 08 7E 10 02 42 0B 08 4E 10 02 1A 05 01 00 00 00 00
```

---

## ⚠️ **Red Team Applications**

1.  **Forced "Transparency"**: Disable ANC in a noisy environment to cause physical distress or distraction.
2.  **Audio Routing Hijack**: Using Ear Detection spoofing to steal audio focus.
3.  **Head Tracking Surveillance**: Infer user activity (nodding, walking, running) from sensor data.
