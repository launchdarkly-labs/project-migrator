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



