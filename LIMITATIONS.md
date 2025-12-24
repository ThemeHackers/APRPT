# System Limitations

## 1. The "Hold Button" Barrier
When a victim presses **Connect** on their iPhone, the screen transitions to a prompt asking them to **"Hold Button"** on the charging case.
*   **Symptom**: The process halts at this screen and cannot proceed further.
*   **Technical Reason**:
    *   To pass this screen, the device must perform an **Authentication Handshake** with the iPhone.
    *   This process allows the iPhone to cryptographically verify the device using private keys embedded in the authentic **Apple W1/H1 chips**.
    *   Since we are using standard generic Bluetooth hardware, we lack these proprietary keys and cannot generate the correct cryptographic response.
*   **Conclusion**: This is a hardware-based security limitation that cannot be bypassed via software at this time (unless the keys are extracted from a real device).

## 2. No Full Pairing
*   This tool functions by **Spoofing** advertisement packets to trick the victim's device into recognizing it as an Apple product.
*   It **cannot** establish a full pairing relationship that would allow for audio streaming or access to advanced settings.
*   The primary goals are **Detection** (HoneyPot) and **Annoyance** (DoS/Spam).

## 3. HoneyPot Lock-on Behavior
*   When the system engages **Lock-on** mode, the victim's iPhone will remain stuck on the "Connecting..." or "Hold Button" screen.
*   The victim may need to manually disable Bluetooth or restart their device if the tool maintains the connection handle indefinitely.
