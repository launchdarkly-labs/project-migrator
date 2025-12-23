# Changelog

## [Initial Release] - 2025-01-29

### Added

- Migrate project settings
- Migrate flag templates
- Migrate context kinds
- Migrate payload filters
- Migrate environments
- Migrate metrics and metric groups
- Migrate segments
- Migrate flags
- Migrate targeting Rules
- Migrate metrics attached to flags

## [1.1.0] - 2025-06-11

### Added

- Match maintainer from old project to new project

### Changed

- Validate environment keys exist

### Fixed

- Wrong API key used when creating project
- Source and target members assigned to wrong list

## [1.2.0] - 2025-06-13

### Added

- Ability to merge one project into another

### Changed

- Migration can be resumed

## [1.3.0] - 2025-06-24

### Added

- Implemented the following optional keys in the app.ini file: MigrateFlagTemplates, MigrateContextKinds, MigratePayloadFilters, MigrateSegments, MigrateMetrics
- REST Adapter class to make it easier handling the API

## [1.4.0] - 2025-06-27

### Added

- Migrate between commercial and federal instances
- Ability to migrate only specific flags
- Ignore built-in pauses (pauses are added to help regulate rate limiting)
- 

## [1.4.1] - 2025-07-25

### Fixed

- Removed attaching metrics to flags as the fucntionality was removed from the LaunchDarkly Platform

## [1.4.2] - 2025-07-30

### Fixed

- Removed reference to getting release pipelines due to incomplete code.

## [1.4.3] - 2025-08-21

### Added

- Exit the app is HTTP requests cannot go through.

## [1.4.4] - 2025-08-21

### Added

- Check to see if `links` item exists in the payload filters payload.

## [1.5.0] - 2025-12-23

### Added

- Added `IgnoreDuplicateFlagNames` and `IgnoreDuplicateSegmentNames` in `app.ini`.

