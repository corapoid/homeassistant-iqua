# iQua Softener - Fixed for HA 2024+

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/corapoid/homeassistant-iqua.svg)](https://github.com/corapoid/homeassistant-iqua/releases)
[![License](https://img.shields.io/github/license/corapoid/homeassistant-iqua.svg)](LICENSE)

Fixed version of the original integration by [@arturzx](https://github.com/arturzx/homeassistant-iqua-softener), compatible with Home Assistant 2024+.

## ⚠️ Why This Fork?

The original integration stopped working with Home Assistant 2024.1+ due to deprecated API calls. This version fixes compatibility issues.

### Changes from original

- ✅ Updated to use `async_forward_entry_setups` (HA 2024+ API)
- ✅ Fixed `async_unload_entry` with `async_unload_platforms`
- ✅ Fixed `AttributeError: 'ConfigEntries' object has no attribute 'async_forward_entry_setup'`
- ✅ Added HACS support

Original repository: https://github.com/arturzx/homeassistant-iqua-softener

---

## About

Home Assistant custom integration for **Viessmann Aquahome 20 Smart** water softener (and compatible EcoWater devices).

The integration connects to EcoWater servers to retrieve real-time water softener data from your iQua-compatible device.

## Key Features

The integration generates nine sensors with 5-second refresh intervals, including:
- Connection status to Ecowater servers
- Device date/time settings
- Salt level percentage
- Water usage metrics (current flow, daily total, daily average)
- Regeneration and salt depletion forecasts
- Available water before next regeneration cycle

The units displayed are set in the application settings.

## Installation

### Option 1: HACS (Recommended)

1. Open HACS in your Home Assistant
2. Click on "Integrations"
3. Click the three dots menu (⋮) in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/corapoid/homeassistant-iqua`
6. Select category: "Integration"
7. Click "Add"
8. Find "iQua Softener (Fixed for HA 2024+)" in HACS
9. Click "Download"
10. Restart Home Assistant
11. Go to Settings → Devices & Services → Add Integration
12. Search for "iQua Softener"
13. Enter your iQua app credentials and device serial number (DSN#)
    - Note: The serial number field is case-sensitive

### Option 2: Manual Installation

1. Copy the `custom_components/iqua_softener` folder to your Home Assistant's config directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "iQua Softener"
5. Enter your iQua app credentials and device serial number (DSN#)
   - Note: The serial number field is case-sensitive

## Configuration

To configure the integration, you'll need:
- **iQua app username** (email)
- **iQua app password**
- **Device serial number** (DSN#)

### How to find your DSN# (Device Serial Number)

1. Open the **iQua app** on your phone
2. Go to **Settings** or tap on your device
3. Look for **DSN#** or **Serial Number**
4. Copy the number **exactly as shown** (case-sensitive, without spaces or dashes)
5. Example format: `7938279241781015` or `DSN1234567890`

⚠️ **Important**: The serial number field is case-sensitive!

## Available Sensors

After setup, you'll have access to these sensors:
- `sensor.iqua_[dsn]_state` - Connection status
- `sensor.iqua_[dsn]_date_time` - Device date/time
- `sensor.iqua_[dsn]_last_regeneration` - Last regeneration timestamp
- `sensor.iqua_[dsn]_out_of_salt_estimated_day` - Estimated salt depletion date
- `sensor.iqua_[dsn]_salt_level` - Salt level percentage
- `sensor.iqua_[dsn]_available_water` - Available water before regeneration
- `sensor.iqua_[dsn]_water_current_flow` - Current water flow rate
- `sensor.iqua_[dsn]_today_water_usage` - Today's water usage
- `sensor.iqua_[dsn]_water_usage_daily_average` - Daily average water usage

## Example Automations

### Low Salt Alert

```yaml
alias: "Alert - Low Salt Level in Water Softener"
trigger:
  - platform: numeric_state
    entity_id: sensor.iqua_[dsn]_salt_level
    below: 20
action:
  - service: notify.mobile_app
    data:
      title: "Uzdatniacz wody"
      message: "Niski poziom soli: {{ states('sensor.iqua_[dsn]_salt_level') }}%"
```

### High Water Usage Alert

```yaml
alias: "Alert - High Water Usage Today"
trigger:
  - platform: numeric_state
    entity_id: sensor.iqua_[dsn]_today_water_usage
    above: 0.5  # 500 liters (0.5 m³)
action:
  - service: notify.mobile_app
    data:
      title: "Zużycie wody"
      message: "Wysokie zużycie dzisiaj: {{ states('sensor.iqua_[dsn]_today_water_usage') }} m³"
```

## Troubleshooting

### "Login failed" error
- Verify credentials in the iQua app (try logging in through the app first)
- Check if your account is active
- Review Home Assistant logs: Settings → System → Logs → filter "iqua"

### "Device not found" error
- Verify DSN# is correct (no spaces, exact match, case-sensitive)
- Ensure device is visible in the iQua app
- Check if device is online

### Sensors not updating
- Verify internet connection on your HA server
- Restart integration: Settings → Integrations → iQua Softener → Reload
- Check if device works in the iQua app
- Review logs for API errors

## Compatible Devices

This integration works with:
- **Viessmann Aquahome 20 Smart**
- EcoWater devices compatible with iQua app
- Water softeners using EcoWater cloud API

## Licensing

This project uses an MIT license. See [LICENSE](LICENSE) file for details.

## Credits

- Original integration: [@arturzx](https://github.com/arturzx/homeassistant-iqua-softener)
- HA 2024+ compatibility fix: [@corapoid](https://github.com/corapoid)
- Built with ❤️ using [Claude Code](https://claude.com/claude-code)
