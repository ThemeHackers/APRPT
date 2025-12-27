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

## 🕵️ **2. Passive Sniffer (Targeted)**
**Command**: `sudo python3 main.py -m sniff -t <MAC> --log-file pol.csv`

### 🖥️ Console Output
```text
[*] Starting Passive Sniffer on hci0... [bold red]TARGETING <MAC>[/bold red]
...
(Only Target Device Appears)
```
### 📊 Result
*   **Log File**: `pol.csv` created containing `Timestamp, MAC, Model, RSSI, Status` history.

---

## 🔍 **3. Advanced Recon**
**Command**: `sudo python3 main.py -m recon -t <MAC>`

### 🖥️ Console Output
```text
...
Device Metadata Report:
- Firmware: 5B58
[bold red][!] VULNERABILITY DETECTED for Firmware 5B58:[/bold red]
    - CVE-2024-27867 (Bluetooth Access Bypass)
```

---

## 🎮 **4. Social Engineering & Control**
**Command**: `sudo python3 main.py -m control -t <MAC>` and `sudo python3 main.py -m advertise --phishing`

### 🎣 Phishing Mode (Advertise)
*   **Console**: `[red]PHISHING MODE ACTIVE. Cycling all models...[/red]`
*   **Physical**: Victim receives a barrage of "Not Your AirPods" popups for varying models (Pro, Max, Beats).

### 📛 Device Rename (Control)
*   **Action**: Select Option 4 ("Rename Device") -> "Connection Failed"
*   **Result**: Target device name changes in Bluetooth settings to "Connection Failed". (May require user action to refresh).

### 😵 Strobe Mode (Control)
*   **Action**: Select Option 6 ("Strobe Mode")
*   **Result**: Victim experiences rapid Disorienting shifts between ANC (Silence) and Transparency (Noise).

### 🔇 Volume Ducking (Hijack)
*   **Action**: `-m hijack -a duck`
*   **Result**: Music volume lowers significantly (Ducking) while active, as if user is speaking.
*   **Smart (Ghost)**: Volume glitches intermittently (random intervals), mimicking a broken sensor.

### 📉 Malicious Audiogram (Hijack)
*   **Action**: `-m hijack -a audiogram`
*   **Result**: Transparency Mode becomes extremely sharp (High-Frequency boost), causing auditory discomfort.
*   **Smart (Boiling Frog)**: The sharpness increases gradually over 10 seconds.

### 📲 Handover Jamming (Hijack)
*   **Action**: `-m hijack -a handover`
*   **Result**: "Move to iPad..." popup appears repeatedly on victim's phone.
*   **Smart (Adaptive)**: Popups appear at irregular intervals to bypass iOS anti-spam logic.

---

## 🤖 **5. Context-Aware Attacks**

### 🚶 Zone Denial (`-m context -a zone`)
*   **Console**: `[!] PROXIMITY ALERT: <MAC> (RSSI: -55)`
*   **Result**: Any Apple device within ~1.5m triggers an immediate disconnect attack.
*   **Smart**: Only triggers if signal is stable > 3 seconds (No false positives from walking past).

### 🏃 Activity Trigger (`-m context -a activity`)
*   **Console**: `[dim]Waiting for A2DP...[/dim]` -> `[!] Activity Detected!`
*   **Result**: Attack (Strobe ANC) fires **only** when the victim puts earbuds in and starts music.

---

## ⛔ **5. Availability & DoS**

### 🔌 L2CAP Flood (`-m dos`)
**Command**: `sudo python3 main.py -m dos -t <MAC>`
*   **Console**: `[blue]Holding 50 connections open...[/blue]`
*   **Physical**: Target device cannot connect to iPhone; user sees "Connection Failed" or endless spinner.

### 🩸 Protocol Fuzzing (`-m bleed -t <MAC>`)
**Command**: `sudo python3 main.py -m bleed -t <MAC>`
*   **Console**: `[yellow]sent 50 fuzz packets...[/yellow]` (Targeting PSM 0x1001)
*   **Physical**: Target headphones may reboot, disconnect, or stop playing audio.

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
