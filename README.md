# iQua Softener - Fixed for HA 2024+

Fixed version of the original integration by arturzx, compatible with Home Assistant 2024+.

## Changes from original

- Updated to use `async_forward_entry_setups` (HA 2024+ API)
- Added proper `async_unload_entry` function with `async_unload_platforms`
- Fixed `AttributeError: 'ConfigEntries' object has no attribute 'async_forward_entry_setup'`

Original repository: https://github.com/arturzx/homeassistant-iqua-softener

---

# iQua Softener Integration for Home Assistant

The iQua softener integration is a custom Home Assistant component that connects to Ecowater servers to retrieve water softener data.

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

1. Copy the `custom_components/iqua_softener` folder to your Home Assistant's config directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "iQua Softener"
5. Enter your iQua app credentials and device serial number (DSN#)
   - Note: The serial number field is case-sensitive

## Configuration

To configure the integration, you'll need:
- iQua app username (email)
- iQua app password
- Device serial number (labeled "DSN#" in the iQua app)

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

## Licensing

This project uses an MIT license.

## Credits

- Original integration: [@arturzx](https://github.com/arturzx)
- HA 2024+ compatibility fix: This fork
