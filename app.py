from __version__ import __version__
import json
import LDMigrate
import LDConfig

config = LDConfig.LDConfig("app.ini")
settings = config.get_config()

ldmigrator = LDMigrate.LDMigrate(
    settings["source_api_token"],
    settings["source_project_key"],
    settings["target_api_token"],
    project_key_target=settings["target_project_key"],
    flags_to_ignore=settings["flags_to_ignore"],
    migration_mode=settings["migration_mode"],
    migrate_flag_templates=settings["migrate_flag_templates"],
    migrate_context_kinds=settings["migrate_context_kinds"],
    migrate_payload_filters=settings["migrate_payload_filters"],
    migrate_segments=settings["migrate_segments"],
    migrate_metrics=settings["migrate_metrics"],
)

result = ldmigrator.migrate()

print(json.dumps(result))
