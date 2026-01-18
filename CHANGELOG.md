# Changelog

All notable changes to this project will be documented in this file.

## [2.1.2] - 2026-01-18

### Fixed
- Race condition on HA restart causing device setup to fail before hub is loaded
- Devices linked to hub now properly wait for hub initialization
- Better handling of orphaned devices when hub entry is removed

## [2.1.1] - 2026-01-17

### Fixed
- Improved error handling for authentication - proper error messages for invalid credentials
- Added timeout handling (30s) for API requests
- Added handling for connection errors, timeouts, and invalid server responses
- Better error messages for 502 server errors

## [2.1.0] - 2026-01-17

### Added
- **Auto-discovery of devices** - When connecting EcoWater account, all registered devices are automatically discovered and added to Home Assistant
- New `/system` API endpoint integration for listing devices

### Changed
- Hub setup now automatically creates device entries for all discovered water softeners
- No longer need to manually add devices after connecting account

## [2.0.3] - 2026-01-17

### Fixed
- Move `no_hub` from error to abort section in translations (was causing missing message)
- Update manifest.json version to match release

## [2.0.2] - 2026-01-17

### Fixed
- Missing menu option labels in config flow - Added `menu_options` translations for hub/legacy selection menu

## [2.0.1] - 2026-01-17

### Fixed
- Missing entity labels (#1) - Added `translations/en.json` file that caused sensor names to display as "n/a" for non-Polish users

## [2.0.0] - 2026-01-17

### Added
- Hub architecture with multi-device support
- Ability to add multiple water softeners under one EcoWater account
- Device linking to hub for centralized management

### Changed
- Complete rewrite of integration architecture
- Improved device registration in Home Assistant

## [1.1.2] - 2026-01-16

### Fixed
- Enhanced logging and availability checks for sensors

## [1.1.1] - 2026-01-15

### Added
- Debug scripts for API troubleshooting (`debug_api.py`, `test_iqua_api.py`)
- Detailed error logging for config flow validation

### Changed
- Improved test script with automatic dependency installation

## [1.1.0] - 2026-01-14

### Fixed
- ConfigEntryNotReady error with retry mechanism
- Improved connection stability

## [1.0.0] - 2026-01-13

### Added
- Initial release
- Basic water softener monitoring
- Sensors: state, salt level, water usage, flow rate, regeneration info
- Polish and English translations
- HACS support
