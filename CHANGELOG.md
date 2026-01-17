# Changelog

All notable changes to this project will be documented in this file.

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
