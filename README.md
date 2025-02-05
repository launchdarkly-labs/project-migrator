# LaunchDarkly Project Migrator

This tool duplicates a project, typically from one account to another. This allows you to merge accounts (1 project at a time), or you can duplicate a project within the same account.

What it migrates:
* Project settings
* Flag templates
* Context kinds
* Payload filters
* Environments
* Metrics and metric groups
* Segments
* Flags
* Targeting Rules
* Metrics attached to flags

What it doesn't migrate:
* Experiments (experiment data cannot be ported at all)
* Integrations (including Webhooks, Flag Triggers, and Code References)
* Big segments
* Relay proxy configurations
* Teams
* Roles
* Account members

Notes:
* SDK / Mobile / Client keys will need to be generated in the new project and updated in the application's configuration
* Try not to make changes to the source project while migrating
* The larger the project, the more memory and time will be required
* Flag statuses will all be reset
* All creation dates will be set at the time of running this script
* Maintainer IDs are not set on any resources
* Historical data cannot be transferred
* NOT idempotent

Future considerations:
* Release pipelines
* Attempt to match target account members to source members and update maintainer IDs
* Teams
* Relevant Roles
* Integrations which do not require human intervention
* Some form of idempotency

Probably will not be considered:
* Integrations requiring human intervention
* Big segments: Environment-specific configuration is required
* Relay proxies: Environment-specific configuration is required
* Experiments: While experiment setups can be easily recreated, the data cannot be migrated from the original experiment to the new one, rendering the new experiment pointless

Reporting:
* 
