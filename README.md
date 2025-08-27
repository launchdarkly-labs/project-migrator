# LaunchDarkly Project Migrator 1.4.4

This tool duplicates a project, typically from one account to another. This allows you to merge accounts (1 project at a time), or you can duplicate a project within the same account.

## Usage:

1. Copy the `app.ini.example` to `app.ini`
2. Edit `app.ini`
3. Set the source and target API keys
4. Set the source project key and optionally the target project key
5. There are additional options you can set under the `[Options]` section
6. Run `python app.py`

### Example app.ini

- Uncommented keys are required
- Commented keys are optional

```
[SourceConfiguration]
SourceApiToken=api-1234567890abcdef
SourceProjectKey=support-service
# SourceIsFederal=false

[TargetConfiguration]
TargetApiToken=api-1234567890abcdef
# TargetProjectKey=fun-little-project
# TargetIsFederal=false

[Options]
MigrateFlagTemplates=true
MigrateContextKinds=true
MigratePayloadFilters=true
MigrateSegments=true
MigrateMetrics=true
# IgnorePauses=false
# Verbose=false
# AllowTargetProjectAlreadyExist=false
# EnvironmentMapping=production:production,dev:dev,qa:staging
# FlagsToIgnore=flag1,flag2,flag3
# FlagsToMigrate=flag1,flag2,flag3
# MigrationMode=MigrateOnly|MigrateRetry|Merge
```

## Configuration Options

### [Options] Section

- **`MigrateFlagTemplates`** (true/false): Include flag templates in migration
- **`MigrateContextKinds`** (true/false): Include context kinds in migratio
- **`MigratePayloadFilters`** (true/false): Include payload filters in migration
- **`MigrateSegments`** (true/false): Include segments in migration
- **`MigrateMetrics`** (true/false): Include metrics and metric groups in migration
- **`IgnorePauses`** (true/false): Skip rate limiting delays (use with caution)
- **`Verbose`** (true/false): Enable detailed HTTP request logging for debugging
- **`AllowTargetProjectAlreadyExist`** (true/false): Continue migration if target project already exists
- **`EnvironmentMapping`** (source:target pairs): Map source environment names to different target names
  - Example: `production:production,dev:development,staging:test`
  - Only environments listed in mapping will be migrated when this option is used
- **`FlagsToIgnore`** (comma-separated): Specific flag keys to skip during migration
- **`FlagsToMigrate`** (comma-separated): Only migrate these specific flag keys (cannot be used with FlagsToIgnore)
- **`MigrationMode`** (MigrateOnly|MigrateRetry|Merge): How to handle existing target projects

## What it migrates:
* Project settings
* Flag templates
* Context kinds
* Payload filters
* Environments
* Metrics and metric groups
* Segments
* Flags
* Targeting Rules
* Attempt to match target account members to source members and update maintainer IDs

## Additional Features
* Restart a failed migration
* Merge one project into another
* Duplicate a project in the same instance
* Select specific flags to copy
* Select specific flags to ignore
* Environment mapping to rename environments during migration
* Verbose logging for debugging API interactions
* Built-in rate limit handling and timing information

## What it doesn't migrate:
* AI Configs
* Experiments (experiment data cannot be ported at all)
* Integrations (including Webhooks, Flag Triggers, and Code References)
* Big segments
* Relay proxy configurations
* Teams
* Roles
* Account members

## Notes:
* When merging, source resources with the same key as the target will be overwritten by the source
* SDK / Mobile / Client keys will be new in the new project, and will need to be updated in the application's configuration
* Try not to make changes to the source project while migrating
* The larger the project, the more memory and time will be required
* Flag statuses will all be reset
* All creation dates will be set at the time of running this script
* Historical data (i.e. Audit log) cannot be transferred
* When using EnvironmentMapping, only environments with a mapping (e.g., `dev:development`) will be migrated
* Environment mapping will skip environments where source and target names differ if the named target environment already exists

## Future considerations:
* AI Configs
* Release pipelines
* Teams
* Relevant Roles
* Integrations which do not require human intervention

## Probably will not be considered:
* Integrations requiring human intervention
* Big segments: Environment-specific configuration is required
* Relay proxies: Environment-specific configuration is required
* Experiments: While experiment setups can be easily recreated, the data cannot be migrated from the original experiment to the new one, rendering the new experiment pointless
* Account members: these must be invites or through SSO
