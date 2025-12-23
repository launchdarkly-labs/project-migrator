import configparser
import os
from LDMigrate import MigrationMode

class LDConfig:
    config_file = ""
    config = None
    required_sections = []
    optional_sections = []
    sections = []
    error_messages = []
    is_valid = False
    settings = {}
    to_bool = {
        "True": True,
        "False": False,
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
    }

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
        settings = self.get_settings()
        if not self.is_valid:
            print("Configuration is not valid:")
            for error in self.error_messages:
                print("  - " + error)
            exit(1)
        return settings

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
        options = {}
        if "Options" in self.sections:
            options = self.config["Options"]

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

        if "MigrationMode" in options:
            if options["MigrationMode"].lower() == "merge":
                if target["TargetProjectKey"] == source["SourceProjectKey"]:
                    self.error_messages.append("Source and target project keys cannot be the same for merge mode.")
                if target["TargetProjectKey"].strip() == "":
                    self.error_messages.append("TargetProjectKey cannot be empty for merge mode.")

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
            "source_is_federal": False,
            "target_api_token": target["TargetApiToken"],
            "target_is_federal": False,
            "ignore_pauses": False,
            "migrate_flag_templates": True,
            "migrate_context_kinds": True,
            "migrate_payload_filters": True,
            "migrate_segments": True,
            "migrate_metrics": True,
            "ignore_duplicate_flags": False,
            "ignore_duplicate_segments": False,
        }
        if "TargetProjectKey" in target:
            settings["target_project_key"] = target["TargetProjectKey"]
        if "MigrateFlagTemplates" in options:
            settings["migrate_flag_templates"] = self.to_bool[options["MigrateFlagTemplates"]]
        if "MigrateContextKinds" in options:
            settings["migrate_context_kinds"] = self.to_bool[options["MigrateContextKinds"]]
        if "MigratePayloadFilters" in options:
            settings["migrate_payload_filters"] = self.to_bool[options["MigratePayloadFilters"]]
        if "MigrateSegments" in options:
            settings["migrate_segments"] = self.to_bool[options["MigrateSegments"]]
        if "MigrateMetrics" in options:
            settings["migrate_metrics"] = self.to_bool[options["MigrateMetrics"]]
        if "IgnoreDuplicateFlagNames" in options:
            settings["ignore_duplicate_flags"] = self.to_bool[options["IgnoreDuplicateFlagNames"]]
        if "IgnoreDuplicateSegmentNames" in options:
            settings["ignore_duplicate_segments"] = self.to_bool[options["IgnoreDuplicateSegmentNames"]]
        if "SourceIsFederal" in source:
            settings["source_is_federal"] = self.to_bool[source["SourceIsFederal"]]
        if "TargetIsFederal" in target:
            settings["target_is_federal"] = self.to_bool[target["TargetIsFederal"]]
        if "IgnorePauses" in options:
            settings["ignore_pauses"] = self.to_bool[options["IgnorePauses"]]
        if "FlagsToIgnore" in options:
            if options["FlagsToIgnore"] != "":
                settings["flags_to_ignore"] = options["FlagsToIgnore"].split(",")
        else:
            settings["flags_to_ignore"] = []
        if "FlagsToMigrate" in options:
            if options["FlagsToMigrate"] != "":
                settings["flags_to_migrate"] = options["FlagsToMigrate"].split(",")
        else:
            settings["flags_to_migrate"] = []
        if "MigrationMode" in options:
            match options["MigrationMode"].lower():
                case "migrateonly":
                    settings["migration_mode"] = MigrationMode.MIGRATE
                case "migrateretry":
                    settings["migration_mode"] = MigrationMode.RETRY
                case "merge":
                    settings["migration_mode"] = MigrationMode.MERGE
                case _:
                    settings["migration_mode"] = MigrationMode.MIGRATE
        else:
            settings["migration_mode"] = MigrationMode.MIGRATE
        if "target_project_key" in settings:
            if settings["target_project_key"] == "":
                settings["target_project_key"] = settings["source_project_key"]
        else:
            settings["target_project_key"] = settings["source_project_key"]

        if len(settings["flags_to_ignore"]) > 0 and len(settings["flags_to_migrate"]) > 0:
            self.error_messages.append("Cannot specify both FlagsToIgnore and FlagsToMigrate.")
            self.is_valid = False
            return
            

        return settings
