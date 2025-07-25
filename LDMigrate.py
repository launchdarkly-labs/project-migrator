import json
import time
from RestAdapter import RestAdapter
from enum import Enum


class MigrationMode(Enum):
    NONE = 0
    MIGRATE = 1
    RETRY = 2
    MERGE = 3


class LDMigrate:
    api_key_src = ""
    api_key_tgt = ""
    project_key_source = ""
    project_key_target = None
    project_name_target = None
    flags_to_ignore = []
    flags_to_migrate = []
    migration_mode = None
    flag_keys = []
    env_keys = []
    source_members = {}
    target_members = {}
    total_context_kinds = 0
    total_payload_filters = 0
    total_environments = 0
    total_metrics = 0
    total_metric_groups = 0
    total_segments = 0
    total_flags = 0
    total_target_rules = 0
    http_source = None
    http_target = None
    migrate_flag_templates = True
    migrate_payload_filters = True
    migrate_context_kinds = True
    migrate_segments = True
    migrate_metrics = True
    ignore_pauses = False

    def __init__(
        self,
        api_key_src,
        project_key_source,
        api_key_tgt,
        project_key_target=None,
        source_is_federal=False,
        target_is_federal=False,
        flags_to_ignore=[],
        flags_to_migrate=[],
        migration_mode=MigrationMode.MIGRATE,
        migrate_flag_templates=True,
        migrate_context_kinds=True,
        migrate_payload_filters=True,
        migrate_segments=True,
        migrate_metrics=True,
        ignore_pauses=False,
    ):
        self.api_key_src = api_key_src
        self.api_key_tgt = api_key_tgt
        self.project_key_source = project_key_source
        if project_key_target is None:
            self.project_key_target = project_key_source
        else:
            self.project_key_target = project_key_target
        if flags_to_ignore is not None:
            self.flags_to_ignore = flags_to_ignore
        if flags_to_migrate is not None:
            self.flags_to_migrate = flags_to_migrate
        self.migration_mode = migration_mode
        src_host = "app.launchdarkly.com"
        if source_is_federal:
            src_host = "app.launchdarkly.us"
        tgt_host = "app.launchdarkly.com"
        if target_is_federal:
            tgt_host = "app.launchdarkly.us"
        self.http_source = RestAdapter(src_host, "v2", self.api_key_src)
        self.http_target = RestAdapter(tgt_host, "v2", self.api_key_tgt)
        self.migrate_flag_templates = migrate_flag_templates
        self.migrate_context_kinds = migrate_context_kinds
        self.migrate_payload_filters = migrate_payload_filters
        self.migrate_segments = migrate_segments
        self.migrate_metrics = migrate_metrics
        self.ignore_pauses = ignore_pauses

    def migrate(self):
        self.get_source_release_pipelines()
        #############################
        # Setting up data structures
        #############################
        print("Getting all flag keys...", end="", flush=True)
        self.flag_keys = self.get_source_flag_keys()
        print("done. Got " + str(len(self.flag_keys)) + " flag keys.", end="\n\n")

        print("Getting all environment keys...", end="", flush=True)
        self.env_keys = self.get_source_environment_keys()
        print("done. Got " + str(len(self.env_keys)) + " environment keys.", end="\n\n")

        print("Getting source members...", end="", flush=True)
        self.source_members = self.get_source_members()
        print("done.", end="\n\n")

        print("Getting target members...", end="", flush=True)
        self.target_members = self.get_target_members()
        print("done.", end="\n\n")

        ##########################
        # Starting migration
        ##########################
        print("Creating target project...", flush=True)
        self.create_target_project()
        print("Done.", end="\n\n")

        if self.migrate_flag_templates:
            print("Updating flag templates...", flush=True)
            self.create_target_flag_templates()
            print("Done.", end="\n\n")
        else:
            print("Skipping flag templates migration per app.ini.", end="\n\n")

        if self.migrate_context_kinds:
            print("Creating context kinds...", flush=True)
            self.create_target_context_kinds()
            print("Done.", end="\n\n")
        else:
            print("Skipping context kinds migration per app.ini.", end="\n\n")

        if self.migrate_payload_filters:
            print("Creating payload filters...", flush=True)
            self.create_target_payload_filters()
            print("Done.", end="\n\n")
        else:
            print("Skipping payload filters migration per app.ini.", end="\n\n")

        print("Creating environments...", flush=True)
        self.create_target_environments()
        print("Done.", end="\n\n")

        if self.migrate_metrics:
            print("Creating metrics...", flush=True)
            self.create_target_metrics()
            print("Done.", end="\n\n")

            print("Creating metric groups...", flush=True)
            self.create_target_metric_groups()
            print("Done.", end="\n\n")
        else:
            print("Skipping metrics migration per app.ini.", end="\n\n")

        if self.migrate_segments:
            print("Creating segments...", flush=True)
            self.create_target_segments()
            print("Done.", end="\n\n")
        else:
            print("Skipping segments migration per app.ini.", end="\n\n")

        print("Creating flags...", flush=True)
        self.create_target_flags()
        print("Done.", end="\n\n")

        print("Creating targeting rules...", flush=True)
        self.create_target_flag_environments()
        print("Done.", end="\n\n")

        return {
            "total_context_kinds": self.total_context_kinds,
            "total_payload_filters": self.total_payload_filters,
            "total_environments": self.total_environments,
            "total_metrics": self.total_metrics,
            "total_metric_groups": self.total_metric_groups,
            "total_segments": self.total_segments,
            "total_flags": self.total_flags,
            "total_target_rules": self.total_target_rules,
        }

    # This function checks to see if rate limiting headers are present
    # and will delay the request if the rate limit is reached

    ##################################################
    # Check if target project exists
    ##################################################

    def target_project_exists(self):
        response = self.http_target.get(
            "/projects/" + self.project_key_target,
        )
        data = json.loads(response.text)

        if "message" in data:
            return False
        return True

    ##################################################
    # Get source project details
    ##################################################

    def get_source_project(self):
        path = "/projects/" + self.project_key_source
        response = self.http_source.get(path)
        data = json.loads(response.text)
        return data

    ##################################################
    # Get source flag templates
    ##################################################

    def get_source_flag_templates(self):
        path = "/projects/" + self.project_key_source + "/flag-templates"
        response = self.http_source.get(path, beta=True, internal=True)
        data = json.loads(response.text)
        return data

    ##################################################
    # Get source flag defaults
    ##################################################

    def get_source_flag_defaults(self):
        path = "/projects/" + self.project_key_source + "/flag-defaults"
        response = self.http_source.get(path, beta=True)
        data = json.loads(response.text)
        return data

    ##################################################
    # Get source experiment settings
    ##################################################

    def get_source_experiment_settings(self):
        path = "/projects/" + self.project_key_source + "/experimentation-settings"
        response = self.http_source.get(path, beta=True)
        data = json.loads(response.text)
        return data

    ##################################################
    # Get source context kinds
    ##################################################

    def get_source_context_kinds(self):
        path = "/projects/" + self.project_key_source + "/context-kinds"
        response = self.http_source.get(path)
        data = json.loads(response.text)
        return data

    ##################################################
    # Get source payload filters
    ##################################################

    def get_source_payload_filters(self):
        payload_filters = []
        path = "/projects/" + self.project_key_source + "/payload-filters?limit=20"
        keep_going = True
        while keep_going:
            response = self.http_source.get(path, beta=True)
            data = json.loads(response.text)

            # Append items to the payload_filters list
            if "items" in data:
                for item in data["items"]:
                    payload_filters.append(item)

            # Check if there is a next page
            if "next" not in data["_links"]:
                keep_going = False
            else:
                path = data["_links"]["next"]["href"].replace("/api/v2", "")

        return payload_filters

    ##################################################
    # Get source environments
    ##################################################

    def get_source_environments(self):
        all_envs = []
        path = "/projects/" + self.project_key_source + "/environments?limit=20"
        keep_going = True
        while keep_going:
            response = self.http_source.get(path)
            data = json.loads(response.text)

            for item in data["items"]:
                all_envs.append(item)

            if "next" not in data["_links"]:
                keep_going = False
            else:
                path = data["_links"]["next"]["href"].replace("/api/v2", "")

        return all_envs

    ##################################################
    # Get source environment keys
    ##################################################

    def get_source_environment_keys(self):
        env_keys = []
        path = "/projects/" + self.project_key_source + "/environments?limit=20"
        keep_going = True
        while keep_going:
            response = self.http_source.get(path)
            data = json.loads(response.text)

            for item in data["items"]:
                env_keys.append(item["key"])

            if "next" not in data["_links"]:
                keep_going = False
            else:
                path = data["_links"]["next"]["href"].replace("/api/v2", "")

        return env_keys

    ##################################################
    # Get target environment keys
    ##################################################

    def get_target_environment_keys(self):
        env_keys = []
        path = "/projects/" + self.project_key_target + "/environments?limit=20"
        keep_going = True
        while keep_going:
            response = self.http_target.get(path)
            data = json.loads(response.text)

            for item in data["items"]:
                env_keys.append(item["key"])

            if "next" not in data["_links"]:
                keep_going = False
            else:
                path = data["_links"]["next"]["href"].replace("/api/v2", "")

        return env_keys

    ##################################################
    # Get source metrics
    ##################################################

    def get_source_metrics(self):
        metrics = []
        path = "/metrics/" + self.project_key_source + "?limit=20"
        keep_going = True
        total = 0
        num = 0
        while keep_going:
            response = self.http_source.get(path)
            data = json.loads(response.text)
            total = data["totalCount"]

            for item in data["items"]:
                num += 1
                res = self.http_source.get(
                    "/metrics/" + self.project_key_source + "/" + item["key"]
                )
                details = json.loads(res.text)
                new_metric = {
                    "key": details["key"],
                    "name": details["name"],
                    "description": details["description"],
                    "kind": details["kind"],
                    "isActive": details["isActive"],
                    "isNumeric": details["isNumeric"],
                    "tags": details["tags"],
                    "randomizationUnits": details["randomizationUnits"],
                    "unitAggregationType": details["unitAggregationType"],
                    "analysisType": details["analysisType"],
                    "eventDefault": details["eventDefault"],
                }
                if "selector" in details:
                    new_metric["selector"] = details["selector"]
                if "urls" in details:
                    new_metric["urls"] = details["urls"]
                if "percentileValue" in details:
                    new_metric["percentileValue"] = details["percentileValue"]
                if "unit" in details:
                    new_metric["unit"] = details["unit"]
                if "eventKey" in details:
                    new_metric["eventKey"] = details["eventKey"]
                if "successCriteria" in details:
                    new_metric["successCriteria"] = details["successCriteria"]
                metrics.append(new_metric)
                if not self.ignore_pauses:
                    time.sleep(0.5)

            if "next" not in data["_links"]:
                keep_going = False
            else:
                path = data["_links"]["next"]["href"].replace("/api/v2", "")

        return metrics

    ##################################################
    # Get source metric groups
    ##################################################

    def get_source_metric_groups(self):
        metric_groups = []
        path = "/projects/" + self.project_key_source + "/metric-groups?limit=20"
        keep_going = True
        total = 0
        num = 0
        while keep_going:
            response = self.http_source.get(path)
            data = json.loads(response.text)
            total = data["totalCount"]

            for item in data["items"]:
                num += 1
                metric_groups.append(item)
                if not self.ignore_pauses:
                    time.sleep(0.5)

            if "next" not in data["_links"]:
                keep_going = False
            else:
                path = data["_links"]["next"]["href"].replace("/api/v2", "")

        return metric_groups

    ##################################################
    # Get source segments
    ##################################################

    def get_source_segments(self):
        limit = 20
        segments = []
        total_segments = 0
        for env in self.env_keys:
            num = 0
            path = (
                "/segments/"
                + self.project_key_source
                + "/"
                + env
                + "?expand=flags&limit="
                + str(limit)
            )
            keep_going = True
            env_segments = []
            while keep_going:
                response = self.http_source.get(path)
                data = json.loads(response.text)

                if data["totalCount"] > 0:
                    for item in data["items"]:
                        num += 1
                        env_segments.append(item)

                # if "items" not in data:
                #     keep_going = False
                # else:
                #     # Update the offset parameter to get the next page
                #     current_offset = len(env_segments)
                #     path = (
                #         "/segments/" + self.project_key_source + "/" + env +
                #         "?limit=" + str(limit) + "&offset=" + str(current_offset)
                #     )
                if "next" not in data["_links"]:
                    keep_going = False
                else:
                    path = data["_links"]["next"]["href"].replace("/api/v2", "")
            total_segments += num
            if num > 0:
                segments.append({"environment": env, "segments": env_segments})
            if not self.ignore_pauses:
                time.sleep(0.5)

        return segments

    ##################################################
    # Get source flags
    ##################################################

    def get_source_flags(self):
        pagination = 50
        flags = []
        num = 0
        path = "/flags/" + self.project_key_source + "?limit=" + str(pagination)
        ignore_flags = True if len(self.flags_to_ignore) > 0 else False
        migrate_flags = True if len(self.flags_to_migrate) > 0 else False
        keep_going = True
        while keep_going:
            response = self.http_source.get(path)
            data = json.loads(response.text)

            for item in data["items"]:
                if ignore_flags and item["key"] in self.flags_to_ignore:
                    continue
                if migrate_flags and item["key"] not in self.flags_to_migrate:
                    continue
                flags.append(item)

            if "next" not in data["_links"]:
                keep_going = False
            else:
                path = data["_links"]["next"]["href"].replace("/api/v2", "")
                num += pagination

        return flags

    ##################################################
    # Get source flag keys
    ##################################################

    def get_source_flag_keys(self):
        pagination = 50
        flag_keys = []
        num = 0
        path = "/flags/" + self.project_key_source + "?limit=" + str(pagination)
        ignore_flags = True if len(self.flags_to_ignore) > 0 else False
        migrate_flags = True if len(self.flags_to_migrate) > 0 else False
        keep_going = True
        while keep_going:
            response = self.http_source.get(path)
            data = json.loads(response.text)

            for item in data["items"]:
                if ignore_flags and item["key"] in self.flags_to_ignore:
                    continue
                if migrate_flags and item["key"] not in self.flags_to_migrate:
                    continue
                flag_keys.append(item["key"])

            if "next" not in data["_links"]:
                keep_going = False
            else:
                path = data["_links"]["next"]["href"].replace("/api/v2", "")
                num += pagination

        return flag_keys

    ##################################################
    # Get source flag details
    ##################################################

    def get_source_flag_details(self, flag_key):
        response = self.http_source.get(
            "/flags/" + self.project_key_source + "/" + flag_key
        )
        data = json.loads(response.text)

        return data

    ##################################################
    # Get source release pipelines
    ##################################################

    def get_source_release_pipelines(self):
        response = self.http_source.get(
            "/projects/" + self.project_key_source + "/release-pipelines", beta=True
        )
        data = json.loads(response.text)
        print(json.dumps(data))
        exit(1)

        return data

    ##################################################
    # Get source members
    ##################################################

    def get_source_members(self):
        keep_going = True
        source_members = {}
        path = "/members"
        while keep_going:
            response = self.http_source.get(path)
            data = json.loads(response.text)
            for member in data["items"]:
                source_members[member["_id"]] = member["email"]

            if "next" not in data["_links"]:
                keep_going = False
            else:
                path = data["_links"]["next"]["href"].replace("/api/v2", "")

        return source_members

    ##################################################
    # Get target members
    ##################################################

    def get_target_members(self):
        keep_going = True
        target_members = {}
        path = "/members"
        while keep_going:
            response = self.http_target.get(path)
            data = json.loads(response.text)
            for member in data["items"]:
                target_members[member["email"]] = member["_id"]

            if "next" not in data["_links"]:
                keep_going = False
            else:
                path = data["_links"]["next"]["href"].replace("/api/v2", "")

        return target_members

    ##################################################
    # Create target project
    ##################################################

    def create_target_project(self):
        project = self.get_source_project()
        project_name = project["name"]
        if self.api_key_tgt == self.api_key_src:
            project_name = project_name + " (copy)"

        payload = {
            "key": self.project_key_target,
            "name": project_name,
            "defaultClientSideAvailability": project["defaultClientSideAvailability"],
            "tags": project["tags"],
        }

        if "namingConvention" in project:
            info_payload = {}
            if "case" in project["namingConvention"]:
                info_payload["case"] = project["namingConvention"]["case"]
            if "prefix" in project["namingConvention"]:
                info_payload["prefix"] = project["namingConvention"]["prefix"]
            payload["namingConvention"] = info_payload

        response = self.http_target.post("/projects", json=payload)

        data = json.loads(response.text)
        if "code" in data:
            if data["code"] == "conflict":
                match self.migration_mode:
                    case MigrationMode.MIGRATE:
                        print("Target project already exists.")
                        exit(1)
                    case MigrationMode.RETRY:
                        print("...target project exists, retrying migration")
                    case MigrationMode.MERGE:
                        print("...target project exists, starting merge")
        else:
            print("...created target project")
        return data

    ##################################################
    # Create target flag templates
    ##################################################

    def create_target_flag_templates(self):
        flag_templates = self.get_source_flag_templates()

        for template in flag_templates["items"]:
            if template["key"] in ["ai-prompt", "ai-model"]:
                continue

            if template["key"] in ["experiment", "migration"]:
                payload = [
                    {"op": "replace", "path": "/tags", "value": template["tags"]}
                ]
            else:
                payload = [
                    {
                        "op": "replace",
                        "path": "/temporary",
                        "value": template["temporary"],
                    },
                    {
                        "op": "replace",
                        "path": "/defaultVariations/onVariation",
                        "value": template["defaultVariations"]["onVariation"],
                    },
                    {
                        "op": "replace",
                        "path": "/defaultVariations/offVariation",
                        "value": template["defaultVariations"]["offVariation"],
                    },
                    {"op": "replace", "path": "/tags", "value": template["tags"]},
                ]
                var_num = 0
                for variation in template["variations"]:
                    if "name" in variation:
                        payload.append(
                            {
                                "op": "add",
                                "path": "/variations/" + str(var_num) + "/name",
                                "value": variation["name"],
                            }
                        )
                    var_num += 1

            response = self.http_target.patch(
                "/projects/"
                + self.project_key_target
                + "/flag-templates/"
                + template["key"],
                json=payload,
                beta=True,
                internal=True,
            )
        print("...updated flag templates")
        return

    ##################################################
    # Create target context kinds
    ##################################################

    def create_target_context_kinds(self):
        context_kinds = self.get_source_context_kinds()
        num_ctx = 0

        for kind in context_kinds["items"]:
            payload = {
                "name": kind["name"],
                "description": kind["description"],
            }
            if "hideInTargeting" in kind:
                payload["hideInTargeting"] = kind["hideInTargeting"]
            if "archived" in kind:
                payload["archived"] = kind["archived"]
            response = self.http_target.put(
                "/projects/"
                + self.project_key_target
                + "/context-kinds/"
                + kind["key"],
                json=payload,
            )
            num_ctx += 1

        exp_settings = self.get_source_experiment_settings()
        payload = {"randomizationUnits": exp_settings["randomizationUnits"]}
        response = self.http_target.put(
            "/projects/" + self.project_key_target + "/experimentation-settings",
            json=payload,
            beta=True,
        )
        self.total_context_kinds = num_ctx
        print("...created " + str(num_ctx) + " context kinds")
        return

    ##################################################
    # Create target payload filters
    ##################################################

    def create_target_payload_filters(self):
        num_filters = 0
        payload_filters = self.get_source_payload_filters()

        for filter in payload_filters:
            payload = {
                "name": filter["name"],
                "key": filter["key"],
                "enabled": filter["enabled"],
                "rules": filter["rules"],
            }
            if "archived" in filter:
                payload["archived"] = filter["archived"]
            if "description" in filter:
                payload["description"] = filter["description"]

            response = self.http_target.post(
                "/projects/" + self.project_key_target + "/payload-filters",
                json=payload,
                beta=True,
            )
            num_filters += 1
        self.total_payload_filters = num_filters
        print("...created " + str(num_filters) + " payload filters")
        return

    ##################################################
    # Create target environments
    ##################################################

    def create_target_environments(self):
        num = 0
        environments = self.get_source_environments()
        existing_keys = self.get_target_environment_keys()
        total_envs = len(environments)

        for env in environments:
            num += 1
            if env["key"] in existing_keys:
                payload = [
                    {"op": "replace", "path": "/name", "value": env["name"]},
                    {"op": "replace", "path": "/color", "value": env["color"]},
                    {
                        "op": "replace",
                        "path": "/defaultTtl",
                        "value": env["defaultTtl"],
                    },
                    {"op": "replace", "path": "/tags", "value": env["tags"]},
                    {
                        "op": "replace",
                        "path": "/secureMode",
                        "value": env["secureMode"],
                    },
                    {
                        "op": "replace",
                        "path": "/defaultTrackEvents",
                        "value": env["defaultTrackEvents"],
                    },
                    {
                        "op": "replace",
                        "path": "/confirmChanges",
                        "value": env["confirmChanges"],
                    },
                    {
                        "op": "replace",
                        "path": "/requireComments",
                        "value": env["requireComments"],
                    },
                    {"op": "replace", "path": "/critical", "value": env["critical"]},
                ]

                response = self.http_target.patch(
                    "/projects/"
                    + self.project_key_target
                    + "/environments/"
                    + env["key"],
                    json=payload,
                )
            else:
                payload = {
                    "name": env["name"],
                    "key": env["key"],
                    "color": env["color"],
                    "defaultTtl": env["defaultTtl"],
                    "tags": env["tags"],
                    "secureMode": env["secureMode"],
                    "defaultTrackEvents": env["defaultTrackEvents"],
                    "confirmChanges": env["confirmChanges"],
                    "requireComments": env["requireComments"],
                    "critical": env["critical"],
                }

                response = self.http_target.post(
                    "/projects/" + self.project_key_target + "/environments",
                    json=payload,
                )

            approvals = [
                {
                    "op": "replace",
                    "path": "/approvalSettings/required",
                    "value": env["approvalSettings"]["required"],
                },
                {
                    "op": "replace",
                    "path": "/approvalSettings/bypassApprovalsForPendingChanges",
                    "value": env["approvalSettings"][
                        "bypassApprovalsForPendingChanges"
                    ],
                },
                {
                    "op": "replace",
                    "path": "/approvalSettings/minNumApprovals",
                    "value": env["approvalSettings"]["minNumApprovals"],
                },
                {
                    "op": "replace",
                    "path": "/approvalSettings/canReviewOwnRequest",
                    "value": env["approvalSettings"]["canReviewOwnRequest"],
                },
                {
                    "op": "replace",
                    "path": "/approvalSettings/canApplyDeclinedChanges",
                    "value": env["approvalSettings"]["canApplyDeclinedChanges"],
                },
                {
                    "op": "replace",
                    "path": "/approvalSettings/requiredApprovalTags",
                    "value": env["approvalSettings"]["requiredApprovalTags"],
                },
                {
                    "op": "replace",
                    "path": "/resourceApprovalSettings/segment/required",
                    "value": env["resourceApprovalSettings"]["segment"]["required"],
                },
                {
                    "op": "replace",
                    "path": "/resourceApprovalSettings/segment/bypassApprovalsForPendingChanges",
                    "value": env["resourceApprovalSettings"]["segment"][
                        "bypassApprovalsForPendingChanges"
                    ],
                },
                {
                    "op": "replace",
                    "path": "/resourceApprovalSettings/segment/minNumApprovals",
                    "value": env["resourceApprovalSettings"]["segment"][
                        "minNumApprovals"
                    ],
                },
                {
                    "op": "replace",
                    "path": "/resourceApprovalSettings/segment/canReviewOwnRequest",
                    "value": env["resourceApprovalSettings"]["segment"][
                        "canReviewOwnRequest"
                    ],
                },
                {
                    "op": "replace",
                    "path": "/resourceApprovalSettings/segment/canApplyDeclinedChanges",
                    "value": env["resourceApprovalSettings"]["segment"][
                        "canApplyDeclinedChanges"
                    ],
                },
                {
                    "op": "replace",
                    "path": "/resourceApprovalSettings/segment/requiredApprovalTags",
                    "value": env["resourceApprovalSettings"]["segment"][
                        "requiredApprovalTags"
                    ],
                },
            ]

            status_code = 0
            while status_code != 200:
                response = self.http_target.patch(
                    "/projects/"
                    + self.project_key_target
                    + "/environments/"
                    + env["key"],
                    json=approvals,
                )
                if response.status_code != 200:
                    if not self.ignore_pauses:
                        time.sleep(0.5)
                status_code = response.status_code

            if num % 10 == 0:
                if not self.ignore_pauses:
                    time.sleep(5)
                print(
                    "...reached "
                    + str(num)
                    + " of "
                    + str(total_envs)
                    + " environments."
                )
        print("...created " + str(num) + " environments")
        self.total_environments = num

    ##################################################
    # Create target metrics
    ##################################################

    def create_target_metrics(self):
        num_metrics = 0
        metrics = self.get_source_metrics()
        for metric in metrics:
            new_metric = metric.copy()
            if "_maintainer" in new_metric:
                del new_metric["_maintainer"]
            if "_maintainer" in metric:
                new_metric["maintainerId"] = self.target_members[
                    metric["_maintainer"]["email"]
                ]
            response = self.http_target.post(
                "/metrics/" + self.project_key_target,
                json=metric,
            )
            if not self.ignore_pauses:
                time.sleep(0.5)
            num_metrics += 1
        print("...created " + str(num_metrics) + " metrics")
        self.total_metrics = num_metrics
        return

    ##################################################
    # Create target metric groups
    ##################################################

    def create_target_metric_groups(self):
        num_groups = 0
        metric_groups = self.get_source_metric_groups()
        for metric_group in metric_groups:
            metrics = []
            for metric in metric_group["metrics"]:
                metrics.append(
                    {
                        "key": metric["key"],
                        "nameInGroup": metric["nameInGroup"],
                    }
                )
            new_group = {
                "key": metric_group["key"],
                "name": metric_group["name"],
                "kind": metric_group["kind"],
                "description": metric_group["description"],
                "maintainerId": metric_group["maintainer"]["key"],
                "tags": metric_group["tags"],
                "metrics": metrics,
            }
            response = self.http_target.post(
                "/projects/" + self.project_key_target + "/metric-groups",
                json=metric_group,
                beta=True,
            )
            num_groups += 1
            if not self.ignore_pauses:
                time.sleep(0.5)
        print("...created " + str(num_groups) + " metric groups")
        self.total_metric_groups = num_groups
        return

    ##################################################
    # Create target segments
    ##################################################

    def create_target_segments(self):
        segments = self.get_source_segments()
        total_segments = 0
        for env in segments:
            add_last = []
            for segment in env["segments"]:
                response = self.http_source.get(
                    "/segments/"
                    + self.project_key_source
                    + "/"
                    + env["environment"]
                    + "/"
                    + segment["key"]
                )
                segment_data = json.loads(response.text)
                payload = {
                    "key": segment_data["key"],
                    "name": segment_data["name"],
                    "tags": segment_data["tags"],
                    "unbounded": False,
                }
                response = self.http_target.post(
                    "/segments/" + self.project_key_target + "/" + env["environment"],
                    json=payload,
                )
                payload = []
                if "description" in segment_data:
                    payload.append(
                        {
                            "op": "add",
                            "path": "/description",
                            "value": segment_data["description"],
                        }
                    )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/included",
                        "value": segment_data["included"],
                    }
                )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/excluded",
                        "value": segment_data["excluded"],
                    }
                )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/includedContexts",
                        "value": segment_data["includedContexts"],
                    }
                )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/excludedContexts",
                        "value": segment_data["excludedContexts"],
                    }
                )
                rules = []
                for_later = False
                for rule in segment_data["rules"]:
                    del rule["_id"]
                    clauses = []
                    for clause in rule["clauses"]:
                        del clause["_id"]
                        if clause["attribute"] == "segmentMatch":
                            for_later = True
                        clauses.append(clause)
                    rule["clauses"] = clauses
                    rules.append(rule)
                if for_later:
                    add_last.append(
                        {
                            "path": env["environment"] + "/" + segment["key"],
                            "payload": {
                                "op": "replace",
                                "path": "/rules",
                                "value": rules,
                            },
                        }
                    )
                else:
                    payload.append(
                        {
                            "op": "replace",
                            "path": "/rules",
                            "value": rules,
                        }
                    )
                response = self.http_target.patch(
                    "/segments/"
                    + self.project_key_target
                    + "/"
                    + env["environment"]
                    + "/"
                    + segment["key"],
                    json=payload,
                )
                if response.status_code != 200:
                    print(
                        "...error updating segment: "
                        + env["environment"]
                        + "/"
                        + segment["key"]
                    )

                total_segments += 1

                if total_segments % 10 == 0:
                    print("...reached " + str(total_segments) + " segments.")
                    if not self.ignore_pauses:
                        time.sleep(2.5)
            for item in add_last:
                response = self.http_target.patch(
                    "/segments/" + self.project_key_target + item["path"],
                    json=item["payload"],
                )

        print("...created " + str(total_segments) + " segments")
        self.total_segments = total_segments
        return

    ##################################################
    # Create target flags
    ##################################################

    def create_target_flags(self):
        flags = self.get_source_flags()

        num = 0
        for flag in flags:
            num += 1
            payload = {
                "key": flag["key"],
                "name": flag["name"],
                "kind": flag["kind"],
                "clientSideAvailability": flag["clientSideAvailability"],
                "variations": flag["variations"],
                "temporary": flag["temporary"],
                "tags": flag["tags"],
            }
            if "defaults" in flag:
                payload["defaults"] = flag["defaults"]
            if "description" in flag:
                payload["description"] = flag["description"]
            if "customProperties" in flag:
                payload["customProperties"] = flag["customProperties"]
            if "_purpose" in flag:
                payload["purpose"] = flag["_purpose"]
            if "_maintainer" in flag:
                if flag["_maintainer"]["email"] in self.target_members:
                    payload["maintainerId"] = self.target_members[
                        flag["_maintainer"]["email"]
                    ]

            response = self.http_target.post(
                "/flags/" + self.project_key_target,
                json=payload,
            )

            update_payload = []
            if "archived" in flag:
                update_payload.append(
                    {"op": "replace", "path": "/archived", "value": flag["archived"]}
                )
            if "deprecated" in flag:
                update_payload.append(
                    {
                        "op": "replace",
                        "path": "/deprecated",
                        "value": flag["deprecated"],
                    }
                )
            if "migrationSettings" in flag:
                update_payload.append(
                    {
                        "op": "replace",
                        "path": "/migrationSettings",
                        "value": flag["migrationSettings"],
                    }
                )

            response = self.http_target.patch(
                "/flags/" + self.project_key_target + "/" + flag["key"],
                json=payload,
            )

            # response = self.http_source.get(
            #     "/projects/"
            #     + self.project_key_source
            #     + "/flags/"
            #     + flag["key"]
            #     + "/measured-rollout-configuration",
            #     beta=True
            # )
            # if response.text != "":
            #     m_data = json.loads(response.text)
            #     if len(m_data["metrics"]) > 0:
            #         metrics = []
            #         for metric in m_data["metrics"]:
            #             metrics.append(metric["key"])
            #         payload = {"metrics": metrics}
            #         response = self.http_target.put(
            #             "/projects/"
            #             + self.project_key_target
            #             + "/flags/"
            #             + flag["key"]
            #             + "/measured-rollout-configuration",
            #             json=payload,
            #             beta=True,
            #         )
            if num % 10 == 0:
                if not self.ignore_pauses:
                    time.sleep(5)
                print("...reached " + str(num) + " flags.")
        print("...created " + str(num) + " flags")
        self.total_flags = num
        return

    ##################################################
    # Create target flag environments
    ##################################################

    def create_target_flag_environments(self):
        retry = 5
        num_flags = len(self.flag_keys)
        error_flags = []
        while retry > 0:
            error_flags = self.create_target_flag_environments_runner(
                retry_flags=error_flags
            )
            if len(error_flags) == 0:
                break
            retry -= 1
        if len(error_flags) > 0:
            print(
                "...the environments for the following flags could not be updated:"
                + str(error_flags)
                + "."
            )
        self.total_target_rules = num_flags - len(error_flags)
        print("...created targeting rules for " + str(num_flags) + " flags")

    ##################################################
    # Create target flag environments runner
    ##################################################

    def create_target_flag_environments_runner(self, retry_flags=None):
        num = 0
        flags_list = []
        if retry_flags:
            flags_list = retry_flags
        else:
            flags_list = self.flag_keys
        error_flags = []

        for flag in flags_list:
            num += 1
            flag_details = self.get_source_flag_details(flag)
            payload = []
            for env in self.env_keys:
                env_details = flag_details["environments"][env]
                payload.append(
                    {
                        "op": "replace",
                        "path": "/environments/" + env + "/on",
                        "value": env_details["on"],
                    }
                )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/environments/" + env + "/archived",
                        "value": env_details["archived"],
                    }
                )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/environments/" + env + "/targets",
                        "value": env_details["targets"],
                    }
                )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/environments/" + env + "/contextTargets",
                        "value": env_details["contextTargets"],
                    }
                )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/environments/" + env + "/fallthrough",
                        "value": env_details["fallthrough"],
                    }
                )
                if "offVariation" in env_details:
                    payload.append(
                        {
                            "op": "replace",
                            "path": "/environments/" + env + "/offVariation",
                            "value": env_details["offVariation"],
                        }
                    )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/environments/" + env + "/prerequisites",
                        "value": env_details["prerequisites"],
                    }
                )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/environments/" + env + "/trackEvents",
                        "value": env_details["trackEvents"],
                    }
                )
                payload.append(
                    {
                        "op": "replace",
                        "path": "/environments/" + env + "/trackEventsFallthrough",
                        "value": env_details["trackEventsFallthrough"],
                    }
                )
                rules_to_del = []
                for i, rule in enumerate(env_details["rules"]):
                    del rule["_id"]
                    need_to_del = []
                    for idx, clause in enumerate(rule["clauses"]):
                        del clause["_id"]
                        if (
                            clause["attribute"] in ["segmentMatch", "not-segmentMatch"]
                            and not self.migrate_segments
                        ):
                            need_to_del.append(idx)
                    if len(need_to_del) > 0:
                        for idx in reversed(need_to_del):
                            del rule["clauses"][idx]
                    if len(rule["clauses"]) == 0:
                        rules_to_del.append(i)
                for x in reversed(rules_to_del):
                    del env_details["rules"][x]
                payload.append(
                    {
                        "op": "replace",
                        "path": "/environments/" + env + "/rules",
                        "value": env_details["rules"],
                    }
                )
            response = self.http_target.patch(
                "/flags/" + self.project_key_target + "/" + flag,
                json=payload,
            )
            if response.status_code != 200:
                error_flags.append(flag)
                print(json.dumps(payload))
                exit(1)
                print("...error updating flag " + flag + ". Will retry later.")
            else:
                print(
                    "...updated environments for flag " + flag + " (" + str(num) + ")"
                )
            if not self.ignore_pauses:
                time.sleep(3)

        return error_flags
