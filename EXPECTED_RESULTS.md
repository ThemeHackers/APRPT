# 🧪 **Expected Test Results**

> **Note**: Since testing on real hardware is not possible at the moment, this document outlines the **expected behavioral and console outputs** for each mode of the APRPT tool.

---

## 📡 **1. Advertise Mode (Spoofing)**
**Command:** `sudo python3 main.py -m advertise`

### 🖥️ Console Output
```text
[*] Mode: advertise
[+] Bluetooth Hardware (hci0) detected successfully.
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID   ┃ Device Name         ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ AirPods             │
│ 2    │ AirPods Pro         │
│ 3    │ AirPods Max         │
│ ...  │ ...                 │
└──────┴─────────────────────┘
Choose a model ID (default=1): 3
[*] Starting Spoofing (AirPods Max) on hci0...
[*] Broadcasting AirPods Max. Look at your iPhone!
[*] Press Ctrl+C to stop.
```

### 📱 Physical Result
*   **Attacker**: Shows a spinning animation. (Blind Broadcast)
*   **Victim (iPhone)**:
    *   ✨ **Popup**: A white setup animation appears ("Not Your AirPods Max").
    *   ❌ **Limit**: "Connect" button may be unresponsive as this is a spoof.

---

## 🕵️ **2. Passive Sniffer**
**Command**: `sudo python3 main.py -m sniff`

### 🖥️ Console Output
```text
[*] Starting Passive Sniffer on hci0...
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┓
┃ MAC               ┃ Model               ┃ Battery (L/R/C)   ┃ Lid Open ┃ RSSI ┃ Last Seen┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━┩
│ 11:22:33:44:55:66 │ AirPods Pro         │ 100%/100%/80%     │ No       │ -45  │ 12:00:01 │
│ AA:BB:CC:DD:EE:FF │ [bold red]AirPods (SPOOF?)[/] │ ?/?/?             │ Yes      │ -30  │ 12:00:05 │
└───────────────────┴─────────────────────┴───────────────────┴──────────┴──────┴──────────┘
```

### 📊 Analyzed Result
*   ✅ **Decoded Data**: Real-time display of nearby Apple devices.
*   ✅ **State Detection**: Shows if the lid is open or closed and exact battery percentages.
*   🚨 **Spoof Detection**: Flags suspicious packets.

---

## 🔍 **3. Recon Mode**
**Command:** `sudo python3 main.py -t <TARGET_MAC> -m recon`

### 🖥️ Console Output
```text
[*] Mode: recon
[*] Target: AA:BB:CC:DD:EE:FF
[+] Connected to AA:BB:CC:DD:EE:FF
[*] Starting Metadata Recon...
[+] Handshake Response: OK
[+] Raw Metadata: 04001d00...
[i] Decoded String content: AirPods Pro - GX8Z... - 5B58
```

### 🎯 Analyzed Result
*   **Model Name**: "AirPods Pro"
*   **Serial Number**: "GX8Z..." (Useful for tracking)
*   **Firmware**: "5B58" (Useful for vulnerability matching)

---

## 🎮 **4. Active Control (Hijack)**
**Command**: `sudo python3 main.py -m control -t <TARGET_MAC>`

### 🖥️ Console Output
```text
[*] Connecting to <TARGET> via L2CAP (PSM 0x1001)...
[+] Connected!
[*] Handshake sent.

Choose Action:
1. Force Transparency (Hear Environment)
2. Force ANC (Silence)
3. Force Off (Normal)

aprpt-control > 1
[*] Sent Noise Control Command: TRANSPARENCY
```

### 👂 Physical Result
*   **Victim**: Suddenly hears outside noise as **Transparency Mode** is forcibly enabled.

---

## 🩸 **5. BLE Fuzzer (Bleed)**
**Command**: `sudo python3 main.py -m bleed`

### 🖥️ Console Output
```text
[*] Mode: bleed
[*] Starting BLE Fuzzer...
[+] Sent 100 packets...
[+] Sent 200 packets...
```

### 💥 Physical Result
*   **Victim**: Nearby devices experience UI lag, battery drain, or Bluetooth stack crashes.

---

## 🕸️ **6. HoneyPot Mode**
**Command**: `sudo python3 main.py -m honeypot`

### 🖥️ Console Output
```text
[*] Mode: honeypot
[*] Broadcasting Connectable Signal...
[!] VICTIM CONNECTED: 68:db:f5:xx:xx:xx
[!] STATUS: LOCKED ON
```

### 🔒 Physical Result
*   **Victim**: iPhone gets stuck on **"Hold Button"** screen.
*   **Attacker**: Successfully logs the victim's MAC address.
