import configparser
import os


class LDConfig:
    config_file = ""
    config = None
    required_sections = []
    optional_sections = []
    sections = []
    error_messages = []
    is_valid = False
    settings = {}

    def __init__(self, config_file):
        if not os.path.isfile(config_file):
            print("File not found: " + config_file)
            exit(1)
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.required_sections = ["SourceConfiguration", "TargetConfiguration"]
        self.optional_sections = ["Options"]

    def get_config(self):
        self.read_config()
        self.validate_config()
        return self.get_settings()

    def read_config(self):
        self.config.read(self.config_file)
        self.sections = self.config.sections()
        return

    def validate_config(self):
        not_found = []
        for section in self.required_sections:
            if section not in self.sections:
                not_found.append(section)
                self.error_messages.append("Section not found: " + section)
        if len(not_found) > 0:
            return

        source = self.config["SourceConfiguration"]
        target = self.config["TargetConfiguration"]

        if not source["SourceProjectKey"]:
            self.error_messages.append("SourceProjectKey is required")
        else:
            if source["SourceProjectKey"] == "":
                self.error_messages.append("SourceProjectKey cannot be empty")
        if not source["SourceApiToken"]:
            self.error_messages.append("SourceApiToken is required")
        else:
            if source["SourceApiToken"] == "":
                self.error_messages.append("SourceApiToken cannot be empty")
        if not target["TargetApiToken"]:
            self.error_messages.append("TargetApiToken is required")
        else:
            if target["TargetApiToken"] == "":
                self.error_messages.append("TargetApiToken cannot be empty")

        if len(self.error_messages) == 0:
            self.is_valid = True
        return

    def get_settings(self):
        if not self.is_valid:
            return

        source = self.config["SourceConfiguration"]
        target = self.config["TargetConfiguration"]
        options = {}
        if "Options" in self.sections:
            options = self.config["Options"]
        settings = {
            "source_project_key": source["SourceProjectKey"],
            "source_api_token": source["SourceApiToken"],
            "target_api_token": target["TargetApiToken"],
        }
        if "TargetProjectKey" in target:
            settings["target_project_key"] = target["TargetProjectKey"]
        if "MigrateFlagTemplates" in options:
            settings["migrate_flag_templates"] = bool(options["MigrateFlagTemplates"])
        if "MigratePayloadFilters" in options:
            settings["migrate_payload_filters"] = bool(options["MigratePayloadFilters"])
        if "MigrateMetrics" in options:
            settings["migrate_metrics"] = bool(options["MigrateMetrics"])
        if "FlagsToIgnore" in options:
            if options["FlagsToIgnore"] != "":
                settings["flags_to_ignore"] = options["FlagsToIgnore"].split(",")

        if "target_project_key" in settings:
            if settings["target_project_key"] == "":
                settings["target_project_key"] = settings["source_project_key"]
        else:
            settings["target_project_key"] = settings["source_project_key"]

        return settings
