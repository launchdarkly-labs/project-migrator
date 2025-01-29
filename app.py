import json
import LDMigrate
import LDConfig


config = LDConfig.LDConfig("app.ini")
settings = config.get_config()

ldmigrator = LDMigrate.LDMigrate(
    settings["SourceApiToken"],
    settings["SourceProjectKey"],
    settings["TargetApiToken"],
    settings["TargetProjectKey"],
)

# ldmigrator = LDMigrate.LDMigrate(
#     "support-service",
#     "fun-little-project",
# )

# project = ldmigrator.create_target_project()
# stuff = ldmigrator.create_target_flag_templates()
# stuff = ldmigrator.create_target_context_kinds()
# stuff = ldmigrator.create_target_payload_filters()
# stuff = ldmigrator.create_target_environments()
# stuff = ldmigrator.create_target_metrics()
# stuff = ldmigrator.create_target_metric_groups()
# stuff = ldmigrator.create_target_segments()
# stuff = ldmigrator.create_target_flags()
# stuff = ldmigrator.create_target_flag_environments()
