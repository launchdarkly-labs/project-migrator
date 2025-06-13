# LaunchDarkly Project Migrator 1.2.0

This tool duplicates a project, typically from one account to another. This allows you to merge accounts (1 project at a time), or you can duplicate a project within the same account.

## Usage:

1. Copy the `app.ini.example` to `app.ini`
2. Edit `app.ini`
3. Set the source and target API keys
4. Set the source project key and optionally the target project key
5. There are additional options you can set under the `[Options]` section
6. Run `python app.py`

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
* Metrics attached to flags
* Attempt to match target account members to source members and update maintainer IDs

## Additional Features
* Restart a failed migration
* Merge one project into another

What it doesn't migrate:
* Experiments (experiment data cannot be ported at all)
* Integrations (including Webhooks, Flag Triggers, and Code References)
* Big segments
* Relay proxy configurations
* Teams
* Roles
* Account members

Notes:
* SDK / Mobile / Client keys will be new in the new project, and will need to be updated in the application's configuration
* Try not to make changes to the source project while migrating
* The larger the project, the more memory and time will be required
* Flag statuses will all be reset
* All creation dates will be set at the time of running this script
* Historical data (i.e. Audit log) cannot be transferred

Future considerations:
* AI Configs
* Release pipelines
* Teams
* Relevant Roles
* Integrations which do not require human intervention

Probably will not be considered:
* Integrations requiring human intervention
* Big segments: Environment-specific configuration is required
* Relay proxies: Environment-specific configuration is required
* Experiments: While experiment setups can be easily recreated, the data cannot be migrated from the original experiment to the new one, rendering the new experiment pointless
