# LaunchDarkly Project Migrator

CURRENTLY IN DEVELOPMENT -- NOT READY FOR PRODUCTION USE

This tool duplicates a project, typically from one account to another. This allows you to merge account (1 project at a time), or you can duplicate a project within the same account.

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
* Release pipelines

What it doesn't migrate:
* Experiments (experiment data cannot be ported at all)
* Integrations (including Webhooks, Flag Triggers, and Code References)
* Big segments
* Relay proxy configurations
* Teams
* Roles
* Account members

Notes:
* Try not to make changes to the source project while migrating
* The larger the project, the more memory and time will be required
* Flag statuses will all be reset
* All creation dates will be set at the time of running this script
* Maintainer IDs are not set on any resources
* Historical data cannot be transferred
* NOT idempotent

Future considerations:
* Attempt to match target account members to source members and update maintainer IDs
* Teams
* Relevant Roles
* Integrations which do not require human intervention

Probably not to be considered:
* Integrations requiring human intervention
* Big segments: Environment-specific configuration is required
* Relay proxies: Environment-specific configuration is required
* Experiments: Data cannot be migrated
