# Denon Signal Info for Home Assistant

Custom Home Assistant integration that exposes the current audio and HDMI
signal information reported by compatible Denon and Marantz receivers.

## Features

- UI config flow with automatic receiver name detection
- support for multiple receivers as separate Home Assistant devices
- one shared local poll for all sensor entities
- configurable polling interval
- HTTPS support, including receivers with self-signed certificates
- Czech and English translations

## Sensors

Each receiver creates these sensors:

- Sample rate
- Input signal
- Audio format / channel layout
- Sound mode
- HDMI resolution
- HDR
- Color space
- Pixel depth

The integration reads the receiver's local XML information endpoint. No cloud
service, Denon account, HEOS account, SSH, or Telnet connection is required.

## Installation

### HACS custom repository

1. In HACS, open **Integrations**.
2. Open the menu and choose **Custom repositories**.
3. Add:

   ```text
   https://github.com/blbeczech82/hass-denon-signal-info
   ```

4. Select category **Integration**.
5. Install **Denon Signal Info**.
6. Restart Home Assistant.

### Manual installation

Copy `custom_components/denon_signal_info` into the Home Assistant
`custom_components` directory and restart Home Assistant.

## Configuration

1. Open **Settings -> Devices & services**.
2. Select **Add integration**.
3. Search for **Denon Signal Info**.
4. Enter the receiver IP address or host name.

Modern receivers normally use:

- port `10443`
- HTTPS enabled
- SSL certificate verification disabled

Use **Configure** on the integration entry to change the polling interval.
Add the integration again to configure another receiver.

## Compatibility

The receiver must provide these local endpoints:

- `/ajax/globals/get_config?type=3`
- `/ajax/general/get_config?type=12`

Initially tested with a Denon AVC-X3700H running firmware
`6420-2105-8116-8080` and Home Assistant `2026.7.4`.
