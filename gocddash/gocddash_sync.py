#!/usr/bin/env python3

import argparse
import datetime
import json
import re
from copy import deepcopy

from gocddash.analysis import data_access, go_client, domain
from gocddash.util import app_config
from gocddash.console_parsers.junit_report_parser import JunitConsoleParser
from gocddash.console_parsers.determine_parser import get_log_parser


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--app-cfg', help='application config')
    parser.add_argument('-f', '--file-source', help='go client file source')
    return parser.parse_args()


def setup_go_client(pargs):
    application_cfg_path = pargs.app_cfg
    app_config.create_app_config(application_cfg_path)

    file_source = pargs.file_source
    if file_source:
        app_config.get_app_config().cfg['GO_SERVER_URL'] = file_source

    go_client.create_go_client(
        app_config.get_app_config().cfg['GO_SERVER_URL'],
        (app_config.get_app_config().cfg['GO_SERVER_USER'], app_config.get_app_config().cfg['GO_SERVER_PASSWD'])
    )


def log(string):
    print(str(datetime.datetime.now()) + " " + string)


class SyncController:
    def __init__(self, db, go, chunk_size=10):
        self.db = db
        self.go = go
        self.chunk_size = chunk_size
        self.to_notify = []
        self.max_to_sync = 500

    def sync(self):
        self.sync_agents()
        self.sync_pipeline_list()
        self.update_sync_rules()
        self.sync_pipelines()
        self.notify_breakers()

    def sync_agents(self):
        """
        Update mapping from uuid to go-agent name in database.
        """
        json_text = self.go.get_agents()
        for agent in json.loads(json_text)["_embedded"]["agents"]:
            self.db.save_agent(agent['uuid'], agent['hostname'])

    def sync_pipeline_list(self):
        json_text = self.go.get_pipeline_groups()
        for group in json.loads(json_text):
            for pipeline in group['pipelines']:
                self.db.save_pipeline(pipeline['name'], group['name'])

    def update_sync_rules(self):
        json_text = self.go.get_pipeline_groups()
        group_for_pipeline = {}
        for group in json.loads(json_text):
            for pipeline in group['pipelines']:
                group_copy = deepcopy(group)
                group_copy['pipelines'] = [pipeline]
                group_for_pipeline[pipeline['name']] = group_copy
        for new_pipeline in self.db.list_new_pipelines():
            self.determine_sync_attributes(
                new_pipeline['pipeline_name'],
                group_for_pipeline[new_pipeline['pipeline_name']]
            )

    def determine_sync_attributes(self, pipeline_name, pipeline_group_structure):
        """
        Update new pipelines, i.e. pipelines where the sync field is NULL in
        the database, if they match some rule. All rules are applied in the
        order given by db.list_pipeline_sync_rules(), so the last rule wins.
        """
        for rule in self.db.list_pipeline_sync_rules():
            assert rule['kind'] == 're'
            nodes = JsonNodes(pipeline_group_structure).nodes
            for key, value in nodes:
                if key == rule['pipeline_groups_field']:
                    if re.search(rule['pattern'], value):
                        kwargs = {}
                        for param in [
                            'sync',
                            'log_parser',
                            'email_notifications'
                        ]:
                            if rule[param] is not None:
                                kwargs[param] = rule[param]
                        self.db.update_pipeline(pipeline_name, **kwargs)

    def sync_pipelines(self):
        for pipeline_name in self.db.get_pipelines_to_sync():
            self.sync_pipeline(pipeline_name)

    def sync_pipeline(self, pipeline_name):
        max_ins = self.max_instance_for_pipeline(pipeline_name)
        wanted_pipeline_instances = self.get_wanted_instances(pipeline_name, max_ins)
        fetched_pipelines_history = self.get_pipeline_history(pipeline_name, wanted_pipeline_instances)
        for pipeline_instance in fetched_pipelines_history:
            self.store_synced_pipeline(pipeline_name, pipeline_instance)
            done = self.sync_stages(pipeline_name, pipeline_instance)
            self.db.store_pipeline_instance_done(pipeline_instance["id"], done)

    def store_synced_pipeline(self, pipeline_name, pipeline_instance):
        pipeline_counter = pipeline_instance["counter"]
        print('Store synced pipeline', pipeline_name, pipeline_counter)
        pipeline_id = pipeline_instance["id"]
        instance = domain.PipelineInstance(
            pipeline_name,
            pipeline_counter,
            pipeline_instance["build_cause"]["trigger_message"],
            pipeline_id
        )
        if not self.db.pipeline_instance_exists(pipeline_name, pipeline_counter):
            self.db.insert_pipeline_instance(instance)

    def sync_stages(self, pipeline_name, pipeline_instance):
        """
        Find all stages for a pipeline instance, and sync them.
        Return whether all were done.
        """
        pipeline_counter = pipeline_instance["counter"]
        pipeline_id = pipeline_instance["id"]
        done = True
        for stage in pipeline_instance['stages']:
            done &= self.sync_stage(pipeline_name, pipeline_counter, pipeline_id, stage)
        return done

    def sync_stage(self, pipeline_name, pipeline_counter, pipeline_id, stage):
        """
        Find any new runs for a stage, and sync them.
        Return whether all were done.
        """
        if not stage['scheduled']:
            return
        stage_name = stage['name']
        current_stage_counter = int(stage['counter'])
        previous_stage_counter = self.db.get_latest_synced_stage(pipeline_id, stage_name)
        stage_counters = range(previous_stage_counter + 1, current_stage_counter + 1)
        done = True
        for stage_counter in stage_counters:
            done &= self.sync_stage_occurrence(
                pipeline_name,
                pipeline_counter,
                pipeline_id,
                stage_name,
                stage_counter
            )
        return done

    def sync_stage_occurrence(self, pipeline_name, pipeline_counter, pipeline_id,
                              stage_name, stage_counter):
        """
        Store information about stage run from go-server and sync its jobs.
        Return whether we were done with the stage.
        """
        stage_occurrence_json = self.go.request_stages_history(pipeline_name, pipeline_counter,
                                                               stage_counter, stage_name)
        stage_occurrence = json.loads(stage_occurrence_json)
        stage_result = stage_occurrence["result"]
        if stage_result == 'Unknown':
            print("  Skipping stage: {} / {} - still in progress".format(
                stage_name, stage_counter))
            return False
        print("  Fetching stage: {} / {}".format(stage_name, stage_counter))
        stage_id = stage_occurrence["id"]

        # Leave for now but a Stage doesn't have a scheduled_date in the API
        timestamp = self.ms_timestamp_to_date(stage_occurrence["jobs"][0]["scheduled_date"])
        stage = domain.Stage(stage_name, stage_occurrence["approved_by"], stage_result,
                             stage_counter, stage_id, timestamp)
        self.db.insert_stage(pipeline_id, stage)
        for job in stage_occurrence['jobs']:
            self.sync_job(pipeline_name, pipeline_counter, stage_id, stage_name, stage_counter, job)
        return True

    def sync_job(self, pipeline_name, pipeline_counter, stage_id, stage_name, stage_counter, job):
        """
        Store information about job and tests from go-server.
        Remember what we should notify breakers about.
        Sync failure info if failure.
        """
        print('sync_job')
        job_name = job['name']
        agent_uuid = job['agent_uuid']
        scheduled_date = self.ms_timestamp_to_date(job['scheduled_date'])
        job_id = job['id']
        job_result = job['result']
        try:
            parser = JunitConsoleParser(pipeline_name, pipeline_counter, stage_counter, stage_name, job_name)
            tests_run, tests_failed, tests_skipped = parser.parse_bar_chart_info()
        except LookupError as error:
            print('Failed parsing test results for {}/{}/{}/{}/{}: {}'.format(
                pipeline_name, pipeline_counter, stage_counter, stage_name, job_name, error
            ))
            tests_run, tests_failed, tests_skipped = 0, 0, 0
        job = domain.Job(job_id, stage_id, job_name, agent_uuid, scheduled_date,
                         job_result, tests_run, tests_failed, tests_skipped)
        self.db.insert_job(stage_id, job)
        print('job result', job_result)

        if job_result != 'Passed' and self.should_notify(pipeline_name):
            stage_failure_info = domain.get_pipeline_head(pipeline_name)
            failure_streak = domain.get_latest_failure_streak(pipeline_name)
            self.to_notify.append((stage_failure_info, failure_streak))

        if job_result == 'Failed' and not self.db.is_failure_downloaded(stage_id):
            self.sync_failure_info(pipeline_counter, pipeline_name,
                                   stage_id, stage_name, stage_counter, job_name)

    def should_notify(self, pipeline_name):
        """
        Are email notifications enabled for this pipeline?
        """
        pipeline = self.db.get_pipeline(pipeline_name)
        return pipeline and pipeline['email_notifications']

    def sync_failure_info(self, pipeline_counter, pipeline_name,
                          stage_id, stage_name, stage_counter, job_name):
        """
        Store failure information from go-server for a given job,
        as extracted from its log parser.
        """
        try:
            log_parser_class = get_log_parser(pipeline_name)
            log_parser = log_parser_class(pipeline_name, pipeline_counter, stage_counter, stage_name, job_name)
            failure_stage = log_parser.get_failure_stage()
            self.db.insert_failure_information(stage_id, failure_stage)
            log_parser.insert_info(stage_id)
        except LookupError as error:
            print("Failed to sync failure info for {}/{}/{}/{}/{}: {}".format(
                pipeline_counter, pipeline_name, stage_name, stage_counter, job_name, error)
            )

    @staticmethod
    def ms_timestamp_to_date(ms):
        """
        Datetime object with truncated fractions of seconds from POSIX timestamp.
        """
        return datetime.datetime.fromtimestamp(ms // 1000)

    def max_instance_for_pipeline(self, pipeline_name):
        """
        Return the highest pipeline counter in Go for the given pipeline.
        """
        try:
            history_json = self.go.request_pipeline_history(pipeline_name)
            return json.loads(history_json)['pipelines'][0]['counter']
        except LookupError:
            return 0

    def get_wanted_instances(self, pipeline_name, counter):
        """
        Get a list of pipeline_counter indicating what to fetch for a pipeline.
        Start at `counter` and go back (but not past 1).
        Don't include instances we already have, don't fetch more than
        self.chunk_size at a time, and never go back more than `self.max_to_sync`
        from the initial value of `counter`.
        """
        oldest_we_want = max(1, counter - self.max_to_sync + 1)
        counters = []
        while len(counters) < self.chunk_size:
            if counter < oldest_we_want:
                break
            if not self.db.pipeline_instance_exists(pipeline_name, counter):
                counters.append(counter)
            counter -= 1
        return counters

    def get_pipeline_history(self, pipeline_name, pipeline_counters):
        """
        Get the history for given pipeline_name, and list of pipeline_counter.
        Since we get the historical information in chunks, we store all historical
        information we get from the go-server in pipeline_cache. If find the
        pipeline counter we're looking for in the pipeline_cache, we get if from
        there, otherwise, we get more history from the go-server.
        """
        def add_to(some_pipeline_cache, offset=[0]):
            """
            Fetch pipeline history and store in a dictionary.
            Increase offset by page_size for each call.
            Return whether we managed to add something or not.
            """
            try:
                history_json = self.go.request_pipeline_history(
                    pipeline_name, offset[0])
            except LookupError:
                return False
            history = json.loads(history_json)
            instances = history.get('pipelines', [])
            for instance in instances:
                some_pipeline_cache[instance['counter']] = instance
            offset[0] += history["pagination"]["page_size"]
            return len(instances) > 0

        pipeline_history = []
        pipeline_cache = {}
        remaining_sorted_counters = sorted(pipeline_counters)
        while remaining_sorted_counters:
            ctr = remaining_sorted_counters[-1]
            if ctr in pipeline_cache:
                pipeline_history.append(pipeline_cache[ctr])
                remaining_sorted_counters.remove(ctr)
            elif pipeline_cache and min(pipeline_cache.keys()) < ctr:
                # If the go-server had this instance, we would have
                # found it by now. It's missing!
                remaining_sorted_counters.remove(ctr)
            else:
                if not add_to(pipeline_cache):
                    break
        return pipeline_history

    def check_notification_needs(self, pipeline_instance):
        pass

    def notify_breakers(self):
        pass


class JsonNodes:
    """
    Parse a Python data structure coming from json, and return a
    list of (key, value) pairs. The keys show the hierarchy using
    dot notation. E.g. {'a': ['b': 6, 'o': 0]} should return
    [('a.b', 6), ('a.o', 0)].
    """
    def __init__(self, json_structure, prefix=None):
        """
        Delegate lists and dicts, and solve the trivial case
        """
        if isinstance(json_structure, list):
            self.nodes = self.json_nodes_list(json_structure, prefix)
        elif isinstance(json_structure, dict):
            self.nodes = self.json_nodes_dict(json_structure, prefix)
        else:
            # If this was neither a list nor a dict, it's a final value,
            # and the path to it is already in the prefix.
            # Return a list like the cases above would.
            self.nodes = [(prefix, json_structure)]

    @classmethod
    def json_nodes_list(cls, json_structure, prefix=None):
        result = []
        for elm in json_structure:
            result.extend(cls(elm, prefix).nodes)
        return result

    @classmethod
    def json_nodes_dict(cls, json_structure, prefix=None):
        result = []
        for key, value in json_structure.items():
            if not prefix:
                new_prefix = key
            else:
                new_prefix = prefix + '.' + key
            result.extend(cls(value, new_prefix).nodes)
        return result


if __name__ == '__main__':
    setup_go_client(parse_args())
    go = go_client.GoClient()
    db = data_access.get_connection(app_config.get_app_config().cfg['DB_PATH'])
    controller = SyncController(db, go)
    log("Starting synchronization.")
    controller.sync()
    log("Synchronization finished.")
    log('Done!')
