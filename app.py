import json
import LDMigrate
import LDConfig
import requests


config = LDConfig.LDConfig("app.ini")
settings = config.get_config()

# ldmigrator = LDMigrate.LDMigrate(
#     settings["source_api_token"],
#     settings["source_project_key"],
#     settings["target_api_token"],
#     settings["target_project_key"],
# )

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

url = (
    "https://app.launchdarkly.com/api/v2/projects/"
    + "cxld-rowdy-limousine"
    + "/flags/release-chart"
    + "/measured-rollout-configuration"
)

headers = {
    "Content-Type": "application/json",
    "Authorization": settings["source_api_token"],
    "LD-API-Version": "beta",
}

# payload = {"metricKeys": metric_keys}

response = requests.get(url, headers=headers)
print(response.text)
