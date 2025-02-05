import json
import LDMigrate
import LDConfig


config = LDConfig.LDConfig("app.ini")
settings = config.get_config()

ldmigrator = LDMigrate.LDMigrate(
    settings["source_api_token"],
    settings["source_project_key"],
    settings["target_api_token"],
    settings["target_project_key"],
)

result = ldmigrator.migrate()

print(result)
