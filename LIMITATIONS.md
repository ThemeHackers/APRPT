# 🚧 **System Limitations**

> **Note**: While APRPT is powerful, it operates within the constraints of generic Bluetooth hardware and the lack of proprietary Apple cryptographic keys.

---

## 🔒 **1. The "Hold Button" Barrier**
*   **Symptom**: Victim's iPhone gets stuck on the **"Hold Button"** screen after connecting.
*   **Reason**: Missing **Apple W1/H1 Chips**.
*   **Explanation**: To proceed past this screen, the device must perform a cryptographic handshake using private keys burned into Apple's silicon. Since we are using generic hardware, we cannot forge this signature.
*   **Impact**: We cannot achieve a "Pairing Success" screen. The "Hold Button" screen is the **maximum theoretical success state** for a software-only spoof.

---

## 👻 **2. Zero-Trust Access**
*   **Limitation**: No audio streaming or settings access.
*   **Reason**: Lack of Link Keys.
*   **Impact**:
    *   We cannot play music through the victim's phone.
    *   We cannot access their iCloud settings.
    *   **Exception**: We *can* hijack audio routing (make them hear *our* audio) via the Hijack module, but we cannot hear *their* audio.

---

## 🪞 **3. Single Adapter Blindness** (`-m sniff`)
*   ⚠️ **Critical Warning**: You cannot sniff your own packets!
*   **Scenario**: Running `-m advertise` and `-m sniff` on the same machine with one adapter (`hci0`).
*   **Result**: The Sniffer will show **Nothing**.
*   **Fix**: Use a second device (iPhone, Android, or another Laptop) to generate the signals you want to sniff.

---

## 🛡️ **4. Root Privilege Requirement**
*   **Error**: `_bluetooth.error: (1, 'Operation not permitted')`
*   **Reason**: Raw HCI socket access requires `CAP_NET_ADMIN`.
*   **Solution**:
    > always run with: `sudo python3 main.py ...`

---

## 🕸️ **5. HoneyPot Lock-on**
*   **Behavior**: When a victim connects to the HoneyPot, their Bluetooth stack may "freeze" on our device.
*   **Impact**: Determining "who" connected is easy, but "disconnecting" them might require them to physically toggle Bluetooth off/on.
