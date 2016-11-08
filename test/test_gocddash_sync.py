import unittest
import json
from collections import OrderedDict

from gocddash.gocddash_sync import SyncController, JsonNodes
from gocddash.analysis.data_access import SQLConnection
from gocddash.analysis.go_client import GoClient
from gocddash.analysis.domain import PipelineInstance


class SyncControllerTests(unittest.TestCase):
    def setUp(self):
        self.db = SQLConnection(':memory:', foreign_keys=False)
        self.go = GoClient('data')
        self.controller = SyncController(self.db, self.go)

    def test_sync_agents_from_empty(self):
        self.controller.sync_agents()

        expected = [
            ("ebed8cc9-0236-407c-af6e-104139e3ca20", "goagent1"),
            ("30834849-e5ff-4674-a69a-ce6c85401de7", "goagent2"),
        ]
        actual = [(row['id'], row['agent_name']) for row in self.db.list_agents()]
        self.assertEqual(actual, expected)

    def test_sync_agents_from_something(self):
        self.db.insert_agent('ebed8cc9-0236-407c-af6e-104139e3ca20', 'edugo1')
        self.db.insert_agent('ebed8cc9-0236-407c-af6e-104139e3ca21', 'edugolr')

        self.controller.sync_agents()

        expected = [
            ("ebed8cc9-0236-407c-af6e-104139e3ca21", "edugolr"),
            ("ebed8cc9-0236-407c-af6e-104139e3ca20", "goagent1"),
            ("30834849-e5ff-4674-a69a-ce6c85401de7", "goagent2"),
        ]
        actual = [(row['id'], row['agent_name']) for row in self.db.list_agents()]
        self.assertEqual(actual, expected)

    def test_sync_pipeline_list_from_empty(self):

        self.controller.sync_pipeline_list()

        expected = [
            ("p1g1", "g1", None, None, None),
            ("p1g2", "g2", None, None, None),
            ("p2g1", "g1", None, None, None),
        ]
        actual = [(row['pipeline_name'], row['pipeline_group'], row['sync'],
                   row['log_parser'], row['email_notifications']) for row in self.db.list_pipelines()]
        self.assertEqual(actual, expected)

    def test_sync_pipeline_list_from_something(self):
        self.db.save_pipeline('p0g0', 'g0')
        self.db.update_pipeline('p0g0', sync=0, log_parser='apa', email_notifications=1)
        self.db.save_pipeline('p1g1', 'g0')
        self.db.update_pipeline('p1g1', sync=1, log_parser='bepa')

        self.controller.sync_pipeline_list()

        expected = [
            ("p0g0", "g0", 0, 'apa', 1),
            ("p1g1", "g1", 1, 'bepa', None),
            ("p1g2", "g2", None, None, None),
            ("p2g1", "g1", None, None, None),
        ]
        actual = [(row['pipeline_name'], row['pipeline_group'], row['sync'],
                   row['log_parser'], row['email_notifications']) for row in self.db.list_pipelines()]
        self.assertEqual(actual, expected)

    def test_sync_pipeline_list_with_rule(self):
        self.db.save_pipeline_sync_rule('.', 1, 'junit', 1)

        self.controller.sync_pipeline_list()
        self.controller.update_sync_rules()

        expected = [
            ("p1g1", "g1", 1, 'junit', 1),
            ("p1g2", "g2", 1, 'junit', 1),
            ("p2g1", "g1", 1, 'junit', 1),
        ]
        actual = [(row['pipeline_name'], row['pipeline_group'], row['sync'],
                   row['log_parser'], row['email_notifications']) for row in self.db.list_pipelines()]
        self.assertEqual(actual, expected)

    def test_sync_pipeline_list_with_rule_but_dont_overwrite(self):
        self.db.save_pipeline('p1g1', 'g9')
        self.db.update_pipeline('p1g1', sync=0, log_parser='other', email_notifications=0)
        self.db.save_pipeline_sync_rule('.', 1, 'junit', 1)

        self.controller.sync_pipeline_list()
        self.controller.update_sync_rules()

        expected = [
            ("p1g1", "g1", 0, 'other', 0),
            ("p1g2", "g2", 1, 'junit', 1),
            ("p2g1", "g1", 1, 'junit', 1),
        ]
        actual = [(row['pipeline_name'], row['pipeline_group'], row['sync'],
                   row['log_parser'], row['email_notifications']) for row in self.db.list_pipelines()]
        self.assertEqual(actual, expected)

    def test_get_wanted_instances_has_nothing(self):
        name = 'p0g0'

        actual = self.controller.get_wanted_instances(name, 7)

        expected = [7, 6, 5, 4, 3, 2, 1]
        self.assertEqual(actual, expected)

    def test_get_wanted_instances_has_some(self):
        name = 'p0g0'
        self.db.save_pipeline(name, 'g0')
        controller = SyncController(self.db, self.go, chunk_size=5)

        class DummyPipeline:
            pipeline_name = name
            pipeline_counter = 4
            trigger_message = 'korv'
            instance_id = 1234
        self.db.insert_pipeline_instance(DummyPipeline())

        actual = controller.get_wanted_instances(name, 7)

        expected = [7, 6, 5, 3, 2]
        self.assertEqual(actual, expected)

    def test_get_wanted_instances_but_there_is_a_limit(self):
        name = 'p0g0'
        self.db.save_pipeline(name, 'g0')

        class DummyPipeline:
            pipeline_name = name
            pipeline_counter = 1994
            trigger_message = 'korv'
            instance_id = 1234

        self.db.insert_pipeline_instance(DummyPipeline())
        controller = SyncController(self.db, self.go, chunk_size=1000)

        actual = controller.get_wanted_instances(name, 2000)

        self.assertEqual(499, len(actual))

    def test_get_pipeline_history_parts_available(self):
        wanted = [7, 6]

        history = self.controller.get_pipeline_history('p0g0', wanted)
        actual = [x['counter'] for x in history]

        self.assertEqual(wanted, actual)

    def test_get_pipeline_history_with_gap(self):
        wanted = [7, 6, 5]

        history = self.controller.get_pipeline_history('gap', wanted)
        actual = [x['counter'] for x in history]

        self.assertEqual([7, 5], actual)

    def test_sync_has_nothing_no_stages(self):
        self.db.save_pipeline('nostages', 'g0')
        self.db.update_pipeline('nostages', sync=1, log_parser='junit')

        self.controller.sync_pipelines()

        self.assertFalse(self.db.pipeline_instance_exists('nostages', 5))
        self.assertTrue(self.db.pipeline_instance_exists('nostages', 6))
        self.assertTrue(self.db.pipeline_instance_exists('nostages', 7))
        self.assertFalse(self.db.pipeline_instance_exists('nostages', 8))

    def test_sync_stage(self):
        pipeline_name = 'p0g0'
        pipeline_counter = 7
        pipeline_id = 47647
        self.db.insert_pipeline_instance(PipelineInstance(
            pipeline_name=pipeline_name,
            pipeline_counter=pipeline_counter,
            trigger_message='',
            instance_id=pipeline_id
        ))
        stage = {
            "result": "Passed",
            "jobs": [{
                "state": "Completed",
                "result": "Passed",
                "name": "defaultJob",
                "id": 59116,
                "scheduled_date": 1476286088191
            }],
            "name": "build",
            "rerun_of_counter": None,
            "approval_type": "success",
            "scheduled": True,
            "operate_permission": True,
            "approved_by": "changes",
            "can_run": True,
            "id": 52700,
            "counter": "1"
        }

        self.controller.sync_stage(
            pipeline_name,
            pipeline_counter,
            pipeline_id,
            stage
        )

        actual_stage_counter = self.db.get_latest_synced_stage(pipeline_id, 'build')
        self.assertEqual(1, actual_stage_counter)

    def test_sync_passed_job(self):
        pipeline_name = 'p0g0'
        pipeline_counter = 7
        stage_id = 52700
        stage_name = 'build'
        stage_counter = 1
        job = {
            'name': 'defaultJob',
            'id': 123,
            'agent_uuid': 'f446f919-856a-488b-bc58-a23341438fef',
            'scheduled_date': 1476704502446,
            'result': 'Passed'
        }
        self.controller.sync_job(pipeline_name,
                                 pipeline_counter,
                                 stage_id,
                                 stage_name,
                                 stage_counter,
                                 job)

        expected = [
            (
                job['id'],
                stage_id,
                job['name'],
                job['agent_uuid'],
                '2016-10-17 13:41:42',
                job['result'],
                13,
                1,
                0
            )
        ]
        jobs = self.db.get_jobs_by_stage_id(stage_id)
        self.assertEqual(expected, [tuple(job) for job in jobs])

    def test_sync_failed_junit_job(self):
        self.db.save_pipeline('p0g0', 'g0')
        self.db.update_pipeline('p0g0', sync=1, log_parser='junit')
        pipeline_name = 'p0g0'
        pipeline_counter = 7
        stage_id = 52700
        stage_name = 'build'
        stage_counter = 1
        job = {
            'name': 'defaultJob',
            'id': 123,
            'agent_uuid': 'f446f919-856a-488b-bc58-a23341438fef',
            'scheduled_date': 1476704502446,
            'result': 'Failed'
        }

        self.controller.sync_job(pipeline_name,
                                 pipeline_counter,
                                 stage_id,
                                 stage_name,
                                 stage_counter,
                                 job)

        expected_jobs = [
            (
                job['id'],
                stage_id,
                job['name'],
                job['agent_uuid'],
                '2016-10-17 13:41:42',
                job['result'],
                13,
                1,
                0
            )
        ]
        jobs = self.db.get_jobs_by_stage_id(stage_id)
        self.assertEqual(expected_jobs, [tuple(job) for job in jobs])
        expected_failure_info = (stage_id, 'TEST')
        failure_info = self.db.is_failure_downloaded(stage_id)
        self.assertEqual(expected_failure_info, (failure_info[1], failure_info[2]))
        expected_junit_info = [('Failure', 'FruitCompany123')]
        junit_info = self.db.get_junit_failure_signature(stage_id)
        self.assertEqual(expected_junit_info, [tuple(junit) for junit in junit_info])

    def test_sync_failed_texttest_job(self):
        self.db.save_pipeline('p0g0', 'g0')
        self.db.update_pipeline('p0g0', sync=1, log_parser='characterize')
        pipeline_name = 'p0g0'
        pipeline_counter = 7
        stage_id = 52700
        stage_name = 'build'
        stage_counter = 1
        job = {
            'name': 'defaultJob',
            'id': 123,
            'agent_uuid': 'f446f919-856a-488b-bc58-a23341438fef',
            'scheduled_date': 1476704502446,
            'result': 'Failed'
        }

        self.controller.sync_job(pipeline_name,
                                 pipeline_counter,
                                 stage_id,
                                 stage_name,
                                 stage_counter,
                                 job)

        expected = [
            (
                job['id'],
                stage_id,
                job['name'],
                job['agent_uuid'],
                '2016-10-17 13:41:42',
                job['result'],
                13,
                1,
                0
            )
        ]
        jobs = self.db.get_jobs_by_stage_id(stage_id)
        self.assertEqual(expected, [tuple(job) for job in jobs])
        expected_failure_info = (stage_id, 'TEST')
        failure_info = self.db.is_failure_downloaded(stage_id)
        self.assertEqual(expected_failure_info, (failure_info[1], failure_info[2]))
        expected_texttest_info = [
            (stage_id, pipeline_counter, 'missing',
             'documentMetadata1062276058_279654258_KaiserKraftEuropaGmbH_0030363209'),
            (stage_id, pipeline_counter, 'missing',
             'primarypres1062276058_279654258_KaiserKraftEuropaGmbH_0030363209'),
            (stage_id, pipeline_counter, 'differences', 'catalogue'),
            (stage_id, pipeline_counter, 'differences', 'routingLog'),
            (stage_id, pipeline_counter, 'differences', 'stdout'),
        ]
        texttest_info = self.db.get_stage_texttest_failures(stage_id)
        self.assertEqual(expected_texttest_info, [tuple(tt)[1:] for tt in texttest_info])

    def test_sync_has_nothing(self):
        self.db.save_pipeline('p0g0', 'g0')
        self.db.update_pipeline('p0g0', sync=1, log_parser='junit')

        self.controller.sync_pipeline('p0g0')

        self.assertTrue(self.db.pipeline_instance_exists('p0g0', 6))
        self.assertTrue(self.db.pipeline_instance_exists('p0g0', 7))

        actual_stage_counter = self.db.get_latest_synced_stage(47621, 'build')
        self.assertEqual(1, actual_stage_counter)
        actual_stage_counter = self.db.get_latest_synced_stage(47647, 'build')
        self.assertEqual(1, actual_stage_counter)

    def test_sync_has_all(self):
        self.db.save_pipeline('p0g0', 'g0')
        self.db.update_pipeline('p0g0', sync=1, log_parser='junit')

        class DummyPipeline:
            pipeline_name = 'p0g0'
            pipeline_counter = 6
            trigger_message = 'korv'
            instance_id = 47621

        self.db.insert_pipeline_instance(DummyPipeline())
        DummyPipeline.pipeline_counter = 7
        DummyPipeline.instance_id = 47647
        self.db.insert_pipeline_instance(DummyPipeline())

        self.controller.sync_pipeline('p0g0')

        self.assertTrue(self.db.pipeline_instance_exists('p0g0', 6))
        self.assertTrue(self.db.pipeline_instance_exists('p0g0', 7))

        actual_stage_counter = self.db.get_latest_synced_stage(47621, 'build')
        self.assertEqual(0, actual_stage_counter)
        actual_stage_counter = self.db.get_latest_synced_stage(47647, 'build')
        self.assertEqual(0, actual_stage_counter)

    def test_sync_has_all_but_newest(self):
        self.db.save_pipeline('p0g0', 'g0')
        self.db.update_pipeline('p0g0', sync=1, log_parser='junit')

        class DummyPipeline:
            pipeline_name = 'p0g0'
            pipeline_counter = 6
            trigger_message = 'korv'
            instance_id = 47621

        self.db.insert_pipeline_instance(DummyPipeline())

        self.controller.sync_pipeline('p0g0')

        self.assertTrue(self.db.pipeline_instance_exists('p0g0', 6))
        self.assertTrue(self.db.pipeline_instance_exists('p0g0', 7))

        actual_stage_counter = self.db.get_latest_synced_stage(47621, 'build')
        self.assertEqual(0, actual_stage_counter)
        actual_stage_counter = self.db.get_latest_synced_stage(47647, 'build')
        self.assertEqual(1, actual_stage_counter)

    def test_sync_has_newest(self):
        self.db.save_pipeline('p0g0', 'g0')
        self.db.update_pipeline('p0g0', sync=1, log_parser='junit')

        class DummyPipeline:
            pipeline_name = 'p0g0'
            pipeline_counter = 7
            trigger_message = 'korv'
            instance_id = 47647

        self.db.insert_pipeline_instance(DummyPipeline())

        self.controller.sync_pipeline('p0g0')

        self.assertTrue(self.db.pipeline_instance_exists('p0g0', 6))
        self.assertTrue(self.db.pipeline_instance_exists('p0g0', 7))

        actual_stage_counter = self.db.get_latest_synced_stage(47621, 'build')
        self.assertEqual(1, actual_stage_counter)
        actual_stage_counter = self.db.get_latest_synced_stage(47647, 'build')
        self.assertEqual(0, actual_stage_counter)

    def test_sync_notification_needed(self):
        pipeline_name = 'failed'
        self.db.save_pipeline(pipeline_name, 'g0')
        self.db.update_pipeline(pipeline_name, sync=1, log_parser='junit', email_notifications=1)
        pipeline_counter = 7
        pipeline_id = 47647
        self.db.insert_pipeline_instance(PipelineInstance(
            pipeline_name=pipeline_name,
            pipeline_counter=pipeline_counter,
            trigger_message='',
            instance_id=pipeline_id
        ))
        stage = {
            "result": "Failed",
            "jobs": [{
                "state": "Completed",
                "result": "Failed",
                "name": "defaultJob",
                "id": 59116,
                "scheduled_date": 1476286088191
            }],
            "name": "build",
            "rerun_of_counter": None,
            "approval_type": "success",
            "scheduled": True,
            "operate_permission": True,
            "approved_by": "changes",
            "can_run": True,
            "id": 52700,
            "counter": "1"
        }

        self.controller.sync_stage(
            pipeline_name,
            pipeline_counter,
            pipeline_id,
            stage
        )

        to_notify = self.controller.to_notify
        self.assertEqual(1, len(to_notify))
        stage_failure_info, result_streak = to_notify[0]
        self.assertEqual('Failed', stage_failure_info.result)
        self.assertEqual(pipeline_name, stage_failure_info.pipeline_name)
        self.assertEqual(pipeline_name, result_streak.pipeline_name)
        self.assertEqual(pipeline_counter, result_streak.fail_counter)

    def test_notify_breaker(self):
        pass


class JsonNodesTests(unittest.TestCase):
    def test_json_nodes(self):
        json_text = """[
  {
    "pipelines": [
      {
        "stages": [
          {
            "name": "up42_stage"
          }
        ],
        "name": "up42",
        "materials": [
          {
            "description": "URL: https://x, Branch: master",
            "type": "Git"
          },
          {
            "description": "URL: https://y, Branch: release_1_2_3",
            "type": "Git"
          }
        ],
        "label": "${COUNT}"
      }
    ],
    "name": "first"
  },
  {
    "name": "second"
  }
]"""
        expected = [
            ('pipelines.stages.name', "up42_stage"),
            ('pipelines.name', "up42"),
            ('pipelines.materials.description', "URL: https://x, Branch: master"),
            ('pipelines.materials.type', "Git"),
            ('pipelines.materials.description', "URL: https://y, Branch: release_1_2_3"),
            ('pipelines.materials.type', "Git"),
            ('pipelines.label', "${COUNT}"),
            ('name', "first"),
            ('name', "second"),
        ]

        structure = json.loads(json_text, object_pairs_hook=OrderedDict)

        actual = JsonNodes(structure).nodes

        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
