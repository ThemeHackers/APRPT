# AAP Definitions (As per AirPods Pro 2 (USB-C) Firmware 7A305)

## Overview and Core Principles

### What is AAP?

**Apple Accessory Protocol (AAP)** is a proprietary application-layer protocol developed by Apple for bidirectional communication between Apple devices (like iPhones, iPads, Macs) and their audio accessories, specifically AirPods and Beats products. AAP enables rich feature control and real-time status monitoring that goes far beyond standard Bluetooth audio profiles.

### Why AAP Exists

Standard Bluetooth audio profiles (A2DP for streaming, AVRCP for basic controls) provide only fundamental audio playback capabilities. Apple developed AAP to enable:

1. **Advanced Feature Control**: Noise cancellation modes, transparency settings, adaptive audio, conversational awareness
2. **Rich Status Monitoring**: Per-component battery levels, ear detection, case status, microphone selection
3. **Deep Customization**: Personalized audio settings, hearing aid configurations, accessibility features
4. **Seamless Integration**: Multi-device switching, head gestures, spatial audio tracking
5. **Ecosystem Lock-in**: Restricting premium features to Apple devices (though LibrePods circumvents this)

### Protocol Architecture

AAP is built on the **Logical Link Control and Adaptation Protocol (L2CAP)**, which is a data protocol layer in the Bluetooth stack. Here's how the layers work:

```
┌─────────────────────────────┐
│   AAP Protocol (Custom)     │  ← Application commands and responses
├─────────────────────────────┤
│   L2CAP (PSM 0x1001)        │  ← Packet segmentation and reassembly
├─────────────────────────────┤
│   Bluetooth Low Energy      │  ← Physical radio layer
└─────────────────────────────┘
```

**Key Concepts:**

- **L2CAP (Logical Link Control and Adaptation Protocol)**: A layer in Bluetooth that provides connection-oriented and connectionless data services with packet segmentation and reassembly capabilities. It allows applications to establish dedicated communication channels.

- **PSM (Protocol/Service Multiplexer)**: A numeric identifier (0x1001 or 4097 for AAP) that tells L2CAP which higher-level protocol should handle incoming data. Think of it as a "port number" for Bluetooth protocols. Multiple applications can use L2CAP simultaneously by using different PSMs.

### Connection Establishment

Unlike standard Bluetooth profiles that connect automatically, AAP requires a specific handshake sequence:

1. **Physical Connection**: Standard Bluetooth pairing establishes the physical link
2. **L2CAP Channel**: An L2CAP connection is opened to PSM 0x1001
3. **AAP Handshake**: A specific packet sequence must be sent, or the AirPods will ignore all subsequent commands
4. **Feature Enablement**: Additional packets may be needed to unlock device-specific features
5. **Notification Registration**: The client must request which events it wants to receive

This multi-stage setup allows Apple to:
- Verify the connected device has appropriate authorization
- Enable/disable features based on the connecting device's capabilities
- Maintain backward compatibility with older AirPods models
- Implement feature restrictions (e.g., adaptive transparency only on certain OS versions)

### Packet Structure Philosophy

AAP uses a simple but extensible packet format:

```
[Header] [Opcode] [Data]
```

**Design Principles:**

1. **Fixed Header**: All packets start with `04 00 04 00`, providing instant packet recognition and synchronization
2. **16-bit Opcodes**: Support for up to 65,536 different commands (little-endian encoding)
3. **Variable-Length Data**: Flexible payload for different command types
4. **Bidirectional**: Same packet format for both commands (host → AirPods) and notifications (AirPods → host)
5. **Stateless Operation**: Each packet is self-contained; no complex session management

This design prioritizes:
- **Simplicity**: Easy to parse and generate packets
- **Extensibility**: New features can be added with new opcodes
- **Efficiency**: Minimal overhead for small status updates
- **Reliability**: Fixed header enables error detection and recovery

## Technical Specifications

AAP runs on top of L2CAP, with a PSM of 0x1001 or 4097.

# Handshake

## Concept: Authentication and Session Initialization

The handshake packet serves as a **session initializer** and **capability announcement**. Without this specific packet, the AirPods firmware enters a "listening but not responding" state—a security measure to ensure only authorized clients can control the device.

**Why a handshake is necessary:**

1. **Security**: Prevents rogue Bluetooth devices from controlling your AirPods
2. **Protocol Versioning**: The handshake may encode protocol version information
3. **Session State**: Initializes internal state machines in the AirPods firmware
4. **Feature Negotiation**: May inform the AirPods about client capabilities

**The Handshake Packet:**

```plaintext
00 00 04 00 01 00 02 00 00 00 00 00 00 00 00 00
```

**Packet Analysis:**
- First 16 bytes: Likely contains protocol version, client type, and initialization flags
- `00 00 04 00`: May indicate protocol version or packet type
- `01 00 02 00`: Could specify client capabilities or feature flags
- Remaining zeros: Reserved for future use or padding

**Important Note**: Apple deliberately hides this packet from PacketLogger (their Bluetooth debugging tool), indicating its sensitivity for their ecosystem lock-in strategy. This was discovered through careful packet capture analysis.

# Setting specific features for AirPods Pro 2

## Concept: Feature Gating and Device Capability Detection

> *may work for airpods 4 anc also, not tested*

Apple implements **progressive feature enablement** based on the connected device's identity and capabilities. This allows them to:

1. **Market Segmentation**: Reserve premium features for newer OS versions or Apple Silicon devices
2. **Hardware Validation**: Ensure the connected device can properly handle advanced features
3. **Gradual Rollout**: Enable features incrementally across firmware updates
4. **A/B Testing**: Test features with specific device configurations

**The Feature Enablement Packet:**

Since apple likes to wall off some features behind specific OS versions, and apple silicon devices, some packets are necessary to enable these features.

I captured the following packet only accidentally, because Apple being Apple decided to hide *this* and *the handshake* from packetlogger, but sometimes it shows up.

*Captured using PacketLogger on an Intel Mac running macOS Sequoia 15.0.1*
```plaintext
04 00 04 00 4d 00 ff 00 00 00 00 00 00 00
```

**What this packet enables:**

This packet enables conversational awareness when playing audio. (CA works without this packet only when no audio is playing)

It also enables the Adaptive Transparency feature. (We can set Adaptive Transparency, but it doesn't respond with the same packet See [Noise Cancellation](#changing-noise-control))

**Technical Explanation:**

- `04 00 04 00`: Standard AAP packet header
- `4d 00`: Opcode 0x004D (decimal 77) - appears to be a "feature unlock" command
- `ff 00 00 00 00 00 00 00`: Feature flags bitmask
  - `0xFF` in the first data byte may enable multiple features simultaneously
  - The specific bit patterns unlock particular capabilities

**Why these features need unlocking:**

- **Conversational Awareness** requires significant audio processing; Apple may want to ensure the connected device can handle the reduced volume notifications
- **Adaptive Transparency** involves real-time audio passthrough modification; older devices might not properly convey these settings

This is a prime example of Apple's "soft" feature restrictions—the hardware is capable, but software gates keep features exclusive to their ecosystem.

# Requesting notifications

## Concept: Event Subscription and Push Notifications

AAP implements a **publish-subscribe pattern** where the client must explicitly register for the types of events it wants to receive. This design offers several advantages:

**Benefits of Explicit Subscription:**

1. **Power Efficiency**: The AirPods don't waste energy broadcasting events nobody is listening for
2. **Bandwidth Optimization**: Reduces unnecessary Bluetooth traffic
3. **Privacy**: Prevents passive monitoring of AirPods state by unauthorized devices
4. **Flexibility**: Different applications can subscribe to different event types
5. **Backward Compatibility**: Newer AirPods with additional events can work with older clients

**The Notification Request Packet:**

This packet is necessary to receive notifications from the AirPods like ear detection, noise control mode, conversational awareness, battery status, etc.

*Captured using PacketLogger on an Intel Mac running macOS Sequoia 15.0.1*
```plaintext
04 00 04 00 0F 00 FF FF FE FF
```

This packet also works.

```plaintext
04 00 04 00 0F 00 FF FF FF FF
```

**Packet Structure Analysis:**

- `04 00 04 00`: Standard AAP header
- `0F 00`: Opcode 0x000F (decimal 15) - "subscribe to notifications" command
- `FF FF FE FF` or `FF FF FF FF`: Subscription bitmask

**Understanding the Bitmask:**

Each bit in the data payload represents a different notification type:
- `FF FF FF FF`: All bits set = subscribe to ALL possible notifications
- `FF FF FE FF`: Nearly all bits set, with one specific notification type disabled (bit cleared)

**Why two versions work:**

The difference (`FE` vs `FF` in the third byte) likely corresponds to a rarely-used notification type. Both packets work because they subscribe to all commonly-needed events like battery status, ear detection, and noise control changes.

**After Subscription:**

Once subscribed, the AirPods will actively push notifications when:
- Battery levels change significantly
- Ear detection state changes (pods inserted/removed)
- Noise control mode is switched
- Conversational awareness is triggered
- Case lid is opened/closed
- Any subscribed event occurs

This notification model ensures the connected device stays synchronized with the AirPods' current state without constant polling, saving power on both ends.

# Notifications

## Battery

### Concept: Multi-Component Power Monitoring

AirPods are unique in having **three independent power systems** (left pod, right pod, and case), each with its own battery, charging circuitry, and state. The battery notification system must convey:

1. **Multiple Battery Levels**: Each component's current charge percentage
2. **Charging States**: Whether each component is charging, discharging, or disconnected
3. **Dynamic Presence**: Not all components are always present (pods might be in/out of case)
4. **Efficient Encoding**: All information in a compact packet

**Design Philosophy:**

The packet uses a **variable-length, self-describing format** where the number of battery components is specified, followed by structured data for each component. This allows:
- Supporting different AirPods models (with/without charging case)
- Handling partial information (e.g., case not present)
- Future extensibility (new components can be added)

**Packet Format:**

AirPods occasionally send battery status packets. The packet format is as follows:

```plaintext
04 00 04 00 04 00 [battery count] ([component] 01 [level] [status] 01) times the battery count
```

**Component Identification (Bitfield):**

| Components | Byte value | Binary | Rationale                           |
|------------|------------|--------|-------------------------------------|
| Right      | 02         | 0010   | Bit 1 - Right is typically primary |
| Left       | 04         | 0100   | Bit 2 - Left is secondary          |
| Case       | 08         | 1000   | Bit 3 - Case is separate component |

The power-of-two encoding allows potential future use as a bitmask for combined status.

**Charging Status:**

| Status       | Byte value | Meaning                                     |
|------------- |------------|---------------------------------------------|
| Unknown      | 00         | State cannot be determined                   |
| Charging     | 01         | Connected to power and actively charging     |
| Discharging  | 02         | Running on battery power                     |
| Disconnected | 04         | Component not connected/present              |

**Battery Level Encoding:**

Direct percentage value (0-100). Values above 100 are typically capped at 100% display.

Example packet from AirPods Pro 2

```plaintext
04 00 04 00 04 00 03 02 01 64 02 01 04 01 63 01 01 08 01 11 02 01
```

| Byte      | Interpretation                     |
|-----------|------------------------------------|
| 7th byte  | Battery Count - 3                  |
| 8th byte  | Battery type - Left                |
| 9th byte  | Spacer, value = 0x01               |
| 10th byte | Battery level 100%                 |
| 11th byte | Battery status - Discharging       |
| 12th byte | Battery component end value = 0x01 |
| 13th byte | Battery type - Right               |
| 14th byte | Spacer, value = 0x01               |
| 15th byte | Battery level 99%                  |
| 16th byte | Battery status - Charging          |
| 17th byte | Battery component end value = 0x01 |
| 18th byte | Battery type - Case                |
| 19th byte | Spacer, value = 0x01               |
| 20th byte | Battery level 17%                  |
| 21st byte | Battery status - Discharging       |
| 22nd byte | Battery component end value = 0x01 |

**Understanding the Example:**

This packet tells us:
- **Left pod**: 100% charged, currently discharging (in use, not in case)
- **Right pod**: 99% charged, currently charging (may have been placed in case)
- **Case**: 17% battery, discharging (providing power to right pod)

The `0x01` spacers and end markers provide structure and may serve as delimiters for parsing variable-length component data.

**Why This Matters:**

This detailed battery information enables:
- Smart charging behavior (don't deplete case unnecessarily)
- User notifications (e.g., "Left pod is low")
- Power management decisions (e.g., enter low-power mode)
- Accurate battery widgets showing all three components

## Noise Control

### Concept: Active Audio Environment Management

Modern AirPods implement **active noise control** using microphones and speakers to modify the ambient sound environment. This involves:

1. **Active Noise Cancellation (ANC)**: Uses destructive interference to cancel external noise by generating inverted sound waves
2. **Transparency Mode**: Amplifies and passes through external sounds using external microphones, creating an "open ear" experience
3. **Adaptive Mode**: Dynamically adjusts between ANC and transparency based on environmental noise levels
4. **Off Mode**: Minimal processing, passive isolation only

**Why Multiple Modes Exist:**

- **Safety**: Transparency mode for situational awareness (crossing streets, conversations)
- **Focus**: ANC for concentration in noisy environments
- **Comfort**: Off mode for users sensitive to pressure sensation from ANC
- **Intelligence**: Adaptive mode automatically adjusts for optimal experience

**Notification Format:**

The AirPods Pro 2 send noise control packets when the noise control mode is changed (either by a stem long press or by the connected device, see [Changing noise control](#changing-noise-control)). The packet format is as follows:

```plaintext
04 00 04 00 09 00 0D [mode] 00 00 00
```

**Mode Values:**

| Noise Control Mode    | Byte value | Audio Processing                                      |
|-----------------------|------------|-------------------------------------------------------|
| Off                   | 01         | Passive isolation only, minimal DSP                   |
| Noise Cancellation    | 02         | Active anti-phase noise cancellation                  |
| Transparency          | 03         | External audio passthrough with amplification         |
| Adaptive Transparency | 04         | Dynamic adjustment based on loud sound detection      |

**Technical Details:**

- `04 00 04 00`: Standard AAP header
- `09 00`: Opcode 0x0009 (control command opcode)
- `0D`: Sub-command 0x0D (noise control mode identifier)
- `[mode]`: The current/requested mode value
- `00 00 00`: Reserved/padding bytes

**Bidirectional Use:**

This packet format works both ways:
- **Notification** (AirPods → Device): Reports current mode after user changes it via stem press
- **Command** (Device → AirPods): Requests mode change from app/UI control

This symmetry simplifies implementation and ensures the device and AirPods stay synchronized.

## Ear Detection

### Concept: Presence Sensing and Automatic Playback Control

AirPods use **capacitive sensors and optical sensors** to detect when they're in a human ear. This enables:

1. **Automatic Pause/Play**: Music stops when you remove an AirPod, resumes when you put it back
2. **Power Management**: Deep sleep when not in use, instant wake when inserted
3. **Microphone Management**: Dynamically assign the microphone to the in-ear pod
4. **Primary Pod Assignment**: The pod in your ear becomes primary for audio routing

**Why Primary/Secondary Matters:**

AirPods have asymmetric roles:
- **Primary Pod**: Receives audio from the phone, handles microphone input, manages the connection
- **Secondary Pod**: Receives audio relayed from the primary pod

When you remove the primary pod, the secondary must quickly become primary to maintain connection and audio continuity. This notification enables seamless handoff.

**Packet Format:**

AirPods send ear detection packets when the ear detection status changes. The packet format is as follows:
```plaintext
04 00 04 00 06 00 [primary pod] [secondary pod]
```

**Key Behavioral Note:**

If primary is removed, mic will be changed and the secondary will be the new primary, so the primary will be the one in the ear, and the packet will be sent again.

**Status Values:**

| Pod Status | Byte value | Physical State                        | Audio Behavior           |
|------------|------------|---------------------------------------|--------------------------|
| In Ear     | 00         | Worn by user, sensors detect presence | Active audio playback    |
| Out of Ear | 01         | Not in ear but outside case           | Paused/standby           |
| In Case    | 02         | Physically in charging case           | Charging, deep sleep     |

**Example Scenarios:**

1. **Both pods in ears**: `00 00` - Normal listening, primary handles audio and mic
2. **Remove right (primary)**: First `01 00`, then quickly `00 01` as left becomes primary
3. **Left in case, right in ear**: `00 02` - Mono audio mode
4. **Both in case**: `02 02` - Charging state, disconnected or disconnecting

**Practical Implications:**

This notification enables:
- Media apps to pause/resume automatically
- Phone calls to switch from AirPods to phone speaker
- Smart re-routing when one pod is low on battery
- Detecting if AirPods were left behind

## Conversational Awareness

AirPods send conversational awareness packets when the person wearing them starts speaking. The packet format is as follows:

```plaintext
04 00 04 00 4B 00 02 00 01 [level]
```

| Level Byte Value    | Meaning                                                 |
|---------------------|---------------------------------------------------------|
| 01/02               | Person Started Speaking; greatly reduce volume          |
| 03                  | Person Stopped Speaking; increase volume back to normal |
| Intermediate values | Intermediate volume levels                              |
| 08/09               | Normal Volume                                           |
### Reading Conversational Awareness State

After requesting notifications, the AirPods send a packet indicating the current state of Conversational Awareness (CA). This packet is only sent once after notifications are requested, not when the CA state is changed.

The packet format is:

```plaintext
04 00 04 00 09 00 28 [status] 00 00 00
```

- `[status]` is a single byte at offset 7 (zero-based), immediately after the header.
    - `0x01` — Conversational Awareness is **enabled**
    - `0x02` — Conversational Awareness is **disabled**
    - Any other value — Unknown/undetermined state

**Example:**
```plaintext
04 00 04 00 09 00 28 01 00 00 00
```
Here, `01` at the 8th byte (offset 7) means CA is enabled.

## Metadata

This packet contains device information like name, model number, etc. The packet format is:

```plaintext
04 00 04 00 1d [strings...]
```

The strings are null-terminated UTF-8 strings in the following order:

1. Bluetooth advertising name (varies in length)
2. Model number 
3. Manufacturer
4. Serial number
5. Firmware version
6. Firmware version 2 (the exact same as before??)
7. Software version   (1.0.0 why would we need it?)
8. App identifier     (com.apple.accessory.updater.app.71 what?)
9. Serial number 1
10. Serial number 2
11. Unknown numeric value
12. Encrypted data
13. Additional encrypted data

Example packet:
```plaintext
040004001d0002d5000400416972506f64732050726f004133303438004170706c6520496e632e0051584e524848595850360036312e313836383034303030323030303030302e323731330036312e313836383034303030323030303030302e3237313300312e302e3000636f6d2e6170706c652e6163636573736f72792e757064617465722e6170702e3731004859394c5432454632364a59004833504c5748444a32364b3000363335373533360089312a6567a5400f84a3ca234947efd40b90d78436ae5946748d70273e66066a2589300035333935303630363400```

The packet contains device identification and version information followed by some encrypted data whose format is not known.
```

# Writing to the AirPods

## Changing Noise Control

We can send a packet to change the noise control mode. The packet format is as follows:

```plaintext
04 00 04 00 09 00 0D [mode] 00 00 00
```

| Noise Control Mode    | Byte value |
|-----------------------|------------|
| Off                   | 01         |
| Noise Cancellation    | 02         |
| Transparency          | 03         |
| Adaptive Transparency | 04         |

The airpods will respond with the same packet after the mode has been changed.

> But if your airpods support Adaptive Transparency, and you haven't sent that [special packet](#setting-specific-features-for-airpods-pro-2) to enable it, the airpods will respond with the same packet but with a different mode (like 0x02).

## Renaming AirPods

We can send a packet to rename the AirPods. The packet format is as follows:

```plaintext
04 00 04 00 1A 00 01 [size] 00 [name]
```

## Toggle case charging sounds

> *This feature is only for cases with a speaker, i.e. the AirPods Pro 2 and the new AirPods 4. Tested only on AirPods Pro 2*

We can send a packet to toggle if sounds should be played when the case is connected to a charger. The packet format is as follows:

```plaintext
12 3A 00 01 00 08 [setting]
```

| Byte Value | Sound |
|------------|-------|
| 00         | On    |
| 01         | Off   |

## Toggle Conversational Awareness

> *This feature is only for AirPods Pro 2 and the new AirPods 4 with ANC. Tested only on AirPods Pro 2*

We can send a packet to toggle Conversational Awareness. If enabled, the AirPods will switch to Transparency mode when the person wearing them starts speaking (and sends packet for notifying the device to reduce volume). The packet format is as follows:

```plaintext
04 00 04 00 09 00 28 [setting] 00 00 00
```

| Byte Value | C.A. |
|------------|------|
| 01         | On   |
| 02         | Off  |

## Adaptive Audio Noise

> *This feature is only for AirPods Pro 2 and the new AirPods 4 with ANC. Tested only on AirPods Pro 2*

The new firmware `7A305` for app2 has a new feature called Adaptive Audio Noise. This allows us to control how much noise is passed through the AirPods when the noise control mode is set to Adaptive. The packet format is as follows:

```plaintext
04 00 04 00 09 00 2E [level] 00 00 00
```

The level can be any value between 0 and 100, 0 to allow maximum noise (i.e. minimum noise filtering), and 100 to filter out more noise.

> This feature is only effective when the noise control mode is set to Adaptive.

*I find it quite funny how I have greater control over the noise control on the AirPods on non-Apple devices than on Apple devices, becuase on Apple Devices, there are just 3 options More Noise (0), Midway through (50), and Less Noise (100), but here I can set any value between 0 and 100.*

## Accessiblity Settings

## Headphone Accomodation
```
04 00 04 00 53 00 84 00 02 02 [Phone] [Media]
[EQ1][EQ2][EQ3][EQ4][EQ5][EQ6][EQ7][EQ8]
duplicated thrice for some reason
```

| Data                | Type          | Value range                 |
|---------------------|---------------|-----------------------------|
| Phone               | Decimal       | 1 (Enabled) or 2 (Disabled) |
| Media               | Decimal       | 1 (Enabled) or 2 (Disabled) |
| EQ                  | Little Endian | 0 to 100                    |

## Customize Transparency mode

```
12 18 00 [enabled]
<left bud>
[EQ1][EQ2][EQ3][EQ4][EQ5][EQ6][EQ7][EQ8]
[Amplification]
[Tone]
[Conversation Boost]
[Ambient Noise Reduction]
<repeat for right bud>
```


All values are formatted as IEEE 754 floats in little endian order.
| Data                    | Type          | Range |
|-------------------------|---------------|-------|
| Enabled                 | IEEE754 Float | 0/1   |
| EQ                      | IEEE754 Float | 0-100 |
| Amplification           | IEEE754 Float | 0-2   |
| Tone                    | IEEE754 Float | 0-2   |
| Conversation Boost      | IEEE754 Float | 0/1   |
| Ambient Noise Reduction | IEEE754 Float | 0-1   |
| Ambient Noise Reduction | IEEE754 Float | 0-1   |

> [!IMPORTANT]
> Also send the [Headphone Accomodation](#headphone-accomodation) after this.


## Configure Stem Long Press

I have noted all the packets sent to configure what the press and hold of the steam should do. The packets sent are specific to the current state. And are probably overwritten everytime the AirPods are connected to a new (apple) device that is not synced with icloud (i think)... So, for non-Apple devices too, the configuration needs to be stored and overwritten everytime the AirPods are connected to the device. That is the only way to keep the configuration.

This is also the only way to control the configuration as the previous state needs to be known, and then the new state can be set. 

The packets sent (based on the previous states) are as follows:

<details>
<summary>Toggling Adaptive</summary>

<code>04 00 04 00 09 00 1A 0B 00 00 00</code> - Turns on Adaptive from O and ANC  
<code>04 00 04 00 09 00 1A 0D 00 00 00</code> - Turns on Adaptive from O and T  
<code>04 00 04 00 09 00 1A 0E 00 00 00</code> - Turns on Adaptive from T and ANC  
<code>04 00 04 00 09 00 1A 0F 00 00 00</code> - Turns on Adaptive from O, T, ANC  

<code>04 00 04 00 09 00 1A 03 00 00 00</code> - Turns off Adaptive from O and ANC (and Adaptive)  
<code>04 00 04 00 09 00 1A 05 00 00 00</code> - Turns off Adaptive from O and T (and Adaptive)  
<code>04 00 04 00 09 00 1A 06 00 00 00</code> - Turns off Adaptive from T and ANC (and Adaptive)  
<code>04 00 04 00 09 00 1A 07 00 00 00</code> - Turns off Adaptive from O, T, ANC (and Adaptive)  

</details>

<details>
<summary>Toggling Transparency</summary>

<code>04 00 04 00 09 00 1A 07 00 00 00</code> - Turns on Transparency from O and ANC  
<code>04 00 04 00 09 00 1A 0D 00 00 00</code> - Turns on Transparency from O and Adaptive  
<code>04 00 04 00 09 00 1A 0E 00 00 00</code> - Turns on Transparency from Adaptive, and ANC  
<code>04 00 04 00 09 00 1A 0F 00 00 00</code> - Turns on Transparency from O and Adaptive and ANC  

<code>04 00 04 00 09 00 1A 03 00 00 00</code> - Turns off Transparency from O and ANC (and Transparency)  
<code>04 00 04 00 09 00 1A 09 00 00 00</code> - Turns off Transparency from O and Adaptive (and Transparency)  
<code>04 00 04 00 09 00 1A 0A 00 00 00</code> - Turns off Transparency from Adaptive, and ANC (and Transparency)  
<code>04 00 04 00 09 00 1A 0B 00 00 00</code> - Turns off Transparency from O and Adaptive and ANC (and Transparency)  

</details>

<details>
<summary>Toggling ANC</summary>

<code>04 00 04 00 09 00 1A 07 00 00 00</code> - Turns on ANC from O, and Transparency  
<code>04 00 04 00 09 00 1A 0B 00 00 00</code> - Turns on ANC from O, and Adaptive  
<code>04 00 04 00 09 00 1A 0E 00 00 00</code> - Turns on ANC from Adaptive, and Transparency  
<code>04 00 04 00 09 00 1A 0F 00 00 00</code> - Turns on ANC from O and Adaptive and Transparency  

<code>04 00 04 00 09 00 1A 05 00 00 00</code> - Turns off ANC from O and Transparency (and ANC)  
<code>04 00 04 00 09 00 1A 09 00 00 00</code> - Turns off ANC from O and Adaptive (and ANC)  
<code>04 00 04 00 09 00 1A 0C 00 00 00</code> - Turns off ANC from Adaptive, and Transparency (and ANC)  
<code>04 00 04 00 09 00 1A 0D 00 00 00</code> - Turns off ANC from O and Adaptive and Transparency (and ANC)  

</details>

<details>
<summary>Toggling O</summary>

<code>04 00 04 00 09 00 1A 07 00 00 00</code> - Turns on O from Transparency, and ANC  
<code>04 00 04 00 09 00 1A 0B 00 00 00</code> - Turns on O from Adaptive, and ANC  
<code>04 00 04 00 09 00 1A 0D 00 00 00</code> - Turns on O from Transparency, and Adaptive  
<code>04 00 04 00 09 00 1A 0F 00 00 00</code> - Turns on O from Transparency, and Adaptive, and ANC  

<code>04 00 04 00 09 00 1A 06 00 00 00</code> - Turns off O from Transparency, and ANC (and O)  
<code>04 00 04 00 09 00 1A 0A 00 00 00</code> - Turns off O from Adaptive, and ANC (and O)  
<code>04 00 04 00 09 00 1A 0C 00 00 00</code> - Turns off O from Transparency, and Adaptive (and O)  
<code>04 00 04 00 09 00 1A 0E 00 00 00</code> - Turns off O from Transparency, and Adaptive, and ANC (and O)  

</details>

> *i do hate apple for not hardcoding these, like there are literally only 4^2 - ${\binom{4}{1}}$ - $\binom{4}{2}$*

# Head Tracking

## Start Tracking

This packet initiates head tracking. When sent, the AirPods begin streaming head tracking data (e.g. orientation and acceleration) for live plotting and analysis.

```plaintext
04 00 04 00 17 00 00 00 10 00 10 00 08 A1 02 42 0B 08 0E 10 02 1A 05 01 40 9C 00 00
```

## Stop Tracking

This packet stops the head tracking data stream.

```plaintext
04 00 04 00 17 00 00 00 10 00 11 00 08 7E 10 02 42 0B 08 4E 10 02 1A 05 01 00 00 00 00
```
## Received Head Tracking Sensor Data

Once tracking is active, the AirPods stream sensor packets with the following common structure:
  
| Field                    | Offset | Length (bytes) |
|--------------------------|--------|----------------|
| orientation 1            | 43     | 2              |
| orientation 2            | 45     | 2              |
| orientation 3            | 47     | 2              |
| Horizontal Acceleration  | 51     | 2              |
| Vertical Acceleration    | 53     | 2              |
