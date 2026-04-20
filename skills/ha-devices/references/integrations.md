# ha-devices — Common Integration Types

Protocol-level integration options and their tradeoffs. Use when choosing how to connect a new class of devices to Home Assistant.

## Zigbee
**Via:** Zigbee2MQTT, ZHA, deCONZ

**Pros:**
- Low power, long battery life
- Mesh networking (devices relay signals)
- Local control, no cloud required
- Wide device compatibility

**Cons:**
- Requires coordinator hardware
- Can have pairing complexity

**Common devices:** Sensors, bulbs, switches, buttons

## Z-Wave
**Via:** Z-Wave JS, Z-Wave JS UI

**Pros:**
- Mature, reliable protocol
- Strong mesh networking
- No WiFi interference (different frequency)
- Good security

**Cons:**
- More expensive devices
- Requires hub/stick
- Regional frequency differences

**Common devices:** Locks, sensors, switches, thermostats

## WiFi
**Via:** Direct integration, Tuya, ESPHome

**Pros:**
- No additional hub needed
- Often cheaper devices
- Easy setup

**Cons:**
- Clogs WiFi network
- Usually requires cloud
- Higher power consumption (no battery)

**Common devices:** Plugs, bulbs, cameras

## Matter/Thread
**Via:** Matter integration

**Pros:**
- Cross-platform standard
- Local control
- Future-proof
- Thread mesh networking

**Cons:**
- New standard, evolving
- Limited device selection currently

## Local API
**Via:** Device-specific integrations

Examples: Philips Hue, LIFX, Shelly, Tasmota

**Pros:**
- Full local control
- Rich features
- Reliable

**Cons:**
- Device-specific setup
