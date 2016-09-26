import unittest
from unittest.mock import MagicMock

from gocddash.console_parsers import characterize_console_parser

# noinspection PyPep8
console_log = """08:17:55.463 [go] Job Started: 2016-07-13 08:17:55 CEST

08:17:55.463 [go] Start to prepare ct-t/2064/runTests/1/defaultJob on build-go-agent012 [/var/lib/go-agent]
08:17:56.174 [go] Cleaning working directory "/var/lib/go-agent/pipelines/ct-t" since stage is configured to clean working directory
08:17:56.174 [go] Start to update materials.

08:17:56.174 [go] Start updating ct-t at revision e11010fdd09309866f34f9d707ec3cf09e65645d from git@git:internet/test/ct-t
08:17:56.176 STDERR: Cloning into '/var/lib/go-agent/pipelines/ct-t/ct-t'...
08:18:07.398 [GIT] Fetch and reset in working directory pipelines/ct-t/ct-t
08:18:07.398 [GIT] Cleaning all unversioned files in working copy
08:18:07.514 [GIT] Cleaning submodule configurations in .git/config
08:18:07.518 [GIT] Fetching changes
08:18:08.564 [GIT] Performing git gc
08:18:08.666 [GIT] Updating working copy to revision e11010fdd09309866f34f9d707ec3cf09e65645d
08:18:08.878 HEAD is now at e11010f Updated go artifacts
08:18:08.879 [GIT] Removing modified files in submodules
08:18:08.909 [GIT] Cleaning all unversioned files in working copy
08:18:09.124 [go] Done.

08:18:09.124 [go] setting environment variable 'GO_SERVER_URL' to value 'https://0.0.0.0:8154/go/'
08:18:09.124 [go] setting environment variable 'GO_TRIGGER_USER' to value 'changes'
08:18:09.124 [go] setting environment variable 'GO_PIPELINE_NAME' to value 'ct-t'
08:18:09.124 [go] setting environment variable 'GO_PIPELINE_COUNTER' to value '2064'
08:18:09.124 [go] setting environment variable 'GO_PIPELINE_LABEL' to value '2064'
08:18:09.124 [go] setting environment variable 'GO_STAGE_NAME' to value 'runTests'
08:18:09.124 [go] setting environment variable 'GO_STAGE_COUNTER' to value '1'
08:18:09.124 [go] setting environment variable 'GO_JOB_NAME' to value 'defaultJob'
08:18:09.124 [go] setting environment variable 'GO_DEPENDENCY_LABEL_UPDATE_plre' to value '2132'
08:18:09.124 [go] setting environment variable 'GO_DEPENDENCY_LOCATOR_UPDATE_plre' to value 'update-plre/2132/build/1'
08:18:09.124 [go] setting environment variable 'GO_REVISION_ct-t' to value 'e11010fdd09309866f34f9d707ec3cf09e65645d'
08:18:09.124 [go] setting environment variable 'GO_TO_REVISION_ct-t' to value 'e11010fdd09309866f34f9d707ec3cf09e65645d'
08:18:09.124 [go] setting environment variable 'GO_FROM_REVISION_ct-t' to value 'e11010fdd09309866f34f9d707ec3cf09e65645d'
08:18:09.124 [go] setting environment variable 'GOCD_PIPELINE_VERSION' to value '1'

08:18:09.130 [go] Start to build ct-t/2064/runTests/1/defaultJob on build-go-agent012 [/var/lib/go-agent]
08:18:09.130 [go] Current job status: passed.

08:18:09.130 [go] Start to execute task: <fetchartifact pipeline="update-plre" stage="build" job="defaultJob" srcdir="go-artifact" dest="upstream_plre" />.
08:18:09.130 [go] Fetching artifact [go-artifact] from [update-plre/2132/build/1/defaultJob]
08:18:09.140 [go] Saved artifact to [pipelines/ct-t/upstream_plre] after verifying the integrity of its contents.
08:18:09.140 [go] Current job status: passed.

08:18:09.140 [go] Start to execute task: <exec command="/home/go/.local/bin/delete_service_logs" workingdir="ct-t" />.
08:18:09.484 deleted /var/log/services
08:18:09.661 [go] Current job status: passed.

08:18:09.661 [go] Start to execute task: <exec command="/bin/bash" workingdir="ct-t" >
<arg>-c</arg>
<arg>/bin/cp ../upstream_plre/go-artifact/*.sbt . | true</arg>
</exec>.
08:18:09.765 [go] Current job status: passed.

08:18:09.765 [go] Start to execute task: <exec command="./go-run-tests.sh" workingdir="ct-t" >
<arg>small</arg>
</exec>.
08:25:29.710 [0m[[0minfo[0m] [0m[0m
08:25:29.710 [0m[[0minfo[0m] [0mDone![0m
08:25:29.710 [0m[[0minfo[0m] [0m[0m
08:25:30.133 [0m[[0minfo[0m] [0mchoosing texttestRoot: Some(/home/go/texttest)[0m
08:25:30.134 [0m[[0minfo[0m] [0mWill install TextTests globally with name List(characterize) under TEXTTEST_ROOT /home/go/texttest[0m
08:25:30.184 [0m[[0minfo[0m] [0mrunning texttest applications List(characterize) in /var/lib/go-agent/pipelines/ct-t/ct-t[0m
08:25:30.216 [0m[[0minfo[0m] [0mfound texttest on PATH at location: Some(/usr/local/bin/texttest)[0m
08:25:30.216 [0m[[0minfo[0m] [0mchoosing texttestRoot: Some(/home/go/texttest)[0m
08:25:30.218 [0m[[0minfo[0m] [0mWill start texttest with this command: List(/usr/local/bin/texttest, -a, characterize, -b, all, -c, /var/lib/go-agent/pipelines/ct-t/ct-t, -d, /var/lib/go-agent/pipelines/ct-t/ct-t/src/it/texttest:/home/go/texttest, -ts, small)[0m
08:25:30.992 [0m[[0minfo[0m] [0m2016-07-13 08:25:30,991 - Using Application ct, checkout /var/lib/go-agent/pipelines/ct-t/ct-t[0m
08:25:31.626 [0m[[0minfo[0m] [0m2016-07-13 08:25:31,625 - Running ct test-suite texttest[0m
08:25:31.626 [0m[[0minfo[0m] [0m2016-07-13 08:25:31,626 -   Running ct test-suite small[0m
08:25:31.626 [0m[[0minfo[0m] [0m2016-07-13 08:25:31,626 -     Running ct test-case warmup[0m
08:25:59.255 [0m[[0minfo[0m] [0m2016-07-13 08:25:59,255 - Comparing differences for ct test-suite texttest[0m
08:25:59.255 [0m[[0minfo[0m] [0m2016-07-13 08:25:59,255 -   Comparing differences for ct test-suite small[0m
08:25:59.257 [0m[[0minfo[0m] [0m2016-07-13 08:25:59,257 -     Comparing differences for ct test-case warmup - SUCCESS! (on stdout.characterize)[0m
08:25:59.325 [0m[[0minfo[0m] [0m2016-07-13 08:25:59,324 -     Running ct test-suite AR01[0m
08:25:59.325 [0m[[0minfo[0m] [0m2016-07-13 08:25:59,325 -       Running ct test-case COMPANY1[0m
08:26:10.236 [0m[[0minfo[0m] [0m2016-07-13 08:26:10,235 -     Comparing differences for ct test-suite AR01[0m
08:26:10.252 [0m[[0minfo[0m] [0m2016-07-13 08:26:10,251 -       Comparing differences for ct test-case COMPANY1 - SUCCESS! (on catalogue.characterize,documentMetadata5481906.characterize,eventsLog.characterize,internalxml_AR01-5481906.characterize,primarypres5481906.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:26:10.281 [0m[[0minfo[0m] [0m2016-07-13 08:26:10,281 -       Running ct test-case COMPANY2[0m
08:26:16.443 [0m[[0minfo[0m] [0m2016-07-13 08:26:16,442 -       Comparing differences for ct test-case COMPANY2 - SUCCESS! (on catalogue.characterize,documentMetadata8912357.characterize,eventsLog.characterize,internalxml_AR01-8912357.characterize,primarypres8912357.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:26:16.482 [0m[[0minfo[0m] [0m2016-07-13 08:26:16,481 -     Running ct test-suite OR01[0m
08:26:16.482 [0m[[0minfo[0m] [0m2016-07-13 08:26:16,482 -       Running ct test-case COMPANY3[0m
08:26:24.696 [0m[[0minfo[0m] [0m2016-07-13 08:26:24,695 -     Comparing differences for ct test-suite OR01[0m
08:26:24.707 [0m[[0minfo[0m] [0m2016-07-13 08:26:24,707 -       Comparing differences for ct test-case COMPANY3 - SUCCESS! (on catalogue.characterize,documentMetadata7384196.characterize,eventsLog.characterize,internalxml_OR01-7384196.characterize,primarypres7384196.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:26:24.736 [0m[[0minfo[0m] [0m2016-07-13 08:26:24,736 -       Running ct test-case COMPANY4[0m
08:26:32.790 [0m[[0minfo[0m] [0m2016-07-13 08:26:32,789 -       Comparing differences for ct test-case COMPANY4 - SUCCESS! (on catalogue.characterize,documentMetadata7384196.characterize,eventsLog.characterize,internalxml_OR01-7384196.characterize,primarypres7384196.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:26:32.818 [0m[[0minfo[0m] [0m2016-07-13 08:26:32,818 -       Running ct test-case COMPANY5[0m
08:26:41.284 [0m[[0minfo[0m] [0m2016-07-13 08:26:41,284 -       Comparing differences for ct test-case COMPANY5 - SUCCESS! (on catalogue.characterize,documentMetadata7384196.characterize,eventsLog.characterize,internalxml_OR01-7384196.characterize,primarypres7384196.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:26:41.329 [0m[[0minfo[0m] [0m2016-07-13 08:26:41,328 -     Running ct test-suite DA01[0m
08:26:41.329 [0m[[0minfo[0m] [0m2016-07-13 08:26:41,329 -       Running ct test-case COMPANY3[0m
08:26:48.530 [0m[[0minfo[0m] [0m2016-07-13 08:26:48,529 -     Comparing differences for ct test-suite DA01[0m
08:26:48.563 [0m[[0minfo[0m] [0m2016-07-13 08:26:48,563 -       Comparing differences for ct test-case COMPANY3 - SUCCESS! (on catalogue.characterize,documentMetadata56910293.characterize,eventsLog.characterize,internalxml_DA01-56910293.characterize,primarypres56910293.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:26:48.598 [0m[[0minfo[0m] [0m2016-07-13 08:26:48,598 -     Running ct test-suite OO01[0m
08:26:48.599 [0m[[0minfo[0m] [0m2016-07-13 08:26:48,598 -       Running ct test-case COMPANY6[0m
08:26:59.500 [0m[[0minfo[0m] [0m2016-07-13 08:26:59,499 -     Comparing differences for ct test-suite OO01[0m
08:26:59.509 [0m[[0minfo[0m] [0m2016-07-13 08:26:59,509 -       Comparing differences for ct test-case COMPANY6 - SUCCESS! (on catalogue.characterize,documentMetadata1273489.characterize,eventsLog.characterize,internalxml_OO01-1273489.characterize,primarypres1273489.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:26:59.542 [0m[[0minfo[0m] [0m2016-07-13 08:26:59,542 -       Running ct test-case COMPANY4[0m
08:27:05.719 [0m[[0minfo[0m] [0m2016-07-13 08:27:05,718 -       Comparing differences for ct test-case COMPANY4 - SUCCESS! (on catalogue.characterize,documentMetadata6589220.characterize,eventsLog.characterize,internalxml_OO01-6589220.characterize,primarypres6589220.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:27:05.754 [0m[[0minfo[0m] [0m2016-07-13 08:27:05,753 -       Running ct test-case COMPANY7[0m
08:27:13.044 [0m[[0minfo[0m] [0m2016-07-13 08:27:13,043 -       Comparing differences for ct test-case COMPANY7 - SUCCESS! (on catalogue.characterize,documentMetadata58729398.characterize,eventsLog.characterize,internalxml_OO01-58729398.characterize,primarypres58729398.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:27:13.122 [0m[[0minfo[0m] [0m2016-07-13 08:27:13,121 -     Running ct test-suite PP01[0m
08:27:13.122 [0m[[0minfo[0m] [0m2016-07-13 08:27:13,122 -       Running ct test-case COMPANY8[0m
08:27:23.600 [0m[[0minfo[0m] [0m2016-07-13 08:27:23,599 -     Comparing differences for ct test-suite PP01[0m
08:27:23.607 [0m[[0minfo[0m] [0m2016-07-13 08:27:23,607 -       Comparing differences for ct test-case COMPANY8 - SUCCESS! (on catalogue.characterize,documentMetadata467329.characterize,documentMetadata12876489.characterize,documentMetadata1728394.characterize,eventsLog.characterize,internalxml_PP01-467329.characterize,internalxml_PP01-12876489.characterize,internalxml_PP01-1728394.characterize,primarypres467329.characterize,primarypres12876489.characterize,primarypres1728394.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:27:23.659 [0m[[0minfo[0m] [0m2016-07-13 08:27:23,658 -       Running ct test-case COMPANY9[0m
08:27:35.684 [0m[[0minfo[0m] [0m2016-07-13 08:27:35,683 -       Comparing differences for ct test-case COMPANY9 - SUCCESS! (on catalogue.characterize,documentMetadata854328.characterize,documentMetadata6164598.characterize,eventsLog.characterize,internalxml_PP01-854328.characterize,internalxml_PP01-6164598.characterize,primarypres854328.characterize,primarypres6164598.characterize,routingLog.characterize,stderr.characterize,stdout.characterize)[0m
08:27:35.735 [0m[[0minfo[0m] [0m2016-07-13 08:27:35,734 -     Running ct test-suite IE01[0m
08:27:35.735 [0m[[0minfo[0m] [0m2016-07-13 08:27:35,735 -       Running ct test-case COMPANY13[0m
08:27:47.982 [0m[[0minfo[0m] [0m2016-07-13 08:27:47,981 -     Comparing differences for ct test-suite IE01[0m
08:27:48.000 [0m[[0minfo[0m] [0m2016-07-13 08:27:47,999 -       Comparing differences for ct test-case COMPANY13 (on catalogue.characterize,eventsLog.characterize,internalxml_IE01-5987313.characterize,routingLog.characterize,stderr.characterize,stdout.characterize,documentMetadata4163489.characterize,internalxml_IE01-4163489.characterize,primarypres4163489.characterize,target_fatturapa_1_1_4163489.characterize)[0m
08:27:48.001 [0m[[0minfo[0m] [0m2016-07-13 08:27:48,001 -       ct test-case COMPANY13 FAILED on build-go-agent012 : new results in internalxml_IE01-5987313, missing results for documentMetadata4163489,internalxml_IE01-4163489,primarypres4163489,target_fatturapa_1_1_4163489, differences in catalogue,routingLog,stdout[0m
08:27:48.011 [0m[[0minfo[0m] [0m2016-07-13 08:27:48,011 - Results:[0m
08:27:48.011 [0m[[0minfo[0m] [0m2016-07-13 08:27:48,011 - [0m
08:27:48.011 [0m[[0minfo[0m] [0m2016-07-13 08:27:48,011 - Tests that did not succeed:[0m
08:27:48.012 [0m[[0minfo[0m] [0m2016-07-13 08:27:48,011 -   ct test-case COMPANY13 FAILED on build-go-agent012 : new results in internalxml_IE01-5987313, missing results for documentMetadata4163489,internalxml_IE01-4163489,primarypres4163489,target_fatturapa_1_1_4163489, differences in catalogue,routingLog,stdout[0m
08:27:48.012 [0m[[0minfo[0m] [0m2016-07-13 08:27:48,012 - [0m
08:27:48.012 [0m[[0minfo[0m] [0m2016-07-13 08:27:48,012 - Tests Run: 13, Failures: 1[0m
08:27:48.492 java.lang.RuntimeException: There were test failures
08:27:48.492 	at org.texttest.sbtplugin.TexttestRunner$$anonfun$runTexttest$1.apply(TexttestRunner.scala:95)
08:27:48.492 	at org.texttest.sbtplugin.TexttestRunner$$anonfun$runTexttest$1.apply(TexttestRunner.scala:75)
08:27:48.492 	at scala.collection.immutable.List.foreach(List.scala:318)
08:27:48.492 	at org.texttest.sbtplugin.TexttestRunner.runTexttest(TexttestRunner.scala:75)
08:27:48.492 	at org.texttest.sbtplugin.TexttestPlugin$$anonfun$projectSettings$14.apply(TexttestPlugin.scala:69)
08:27:48.492 	at org.texttest.sbtplugin.TexttestPlugin$$anonfun$projectSettings$14.apply(TexttestPlugin.scala:63)
08:27:48.492 	at scala.Function1$$anonfun$compose$1.apply(Function1.scala:47)
08:27:48.492 	at sbt.$tilde$greater$$anonfun$$u2219$1.apply(TypeFunctions.scala:40)
08:27:48.492 	at sbt.std.Transform$$anon$4.work(System.scala:63)
08:27:48.492 	at sbt.Execute$$anonfun$submit$1$$anonfun$apply$1.apply(Execute.scala:226)
08:27:48.492 	at sbt.Execute$$anonfun$submit$1$$anonfun$apply$1.apply(Execute.scala:226)
08:27:48.492 	at sbt.ErrorHandling$.wideConvert(ErrorHandling.scala:17)
08:27:48.492 	at sbt.Execute.work(Execute.scala:235)
08:27:48.492 	at sbt.Execute$$anonfun$submit$1.apply(Execute.scala:226)
08:27:48.493 	at sbt.Execute$$anonfun$submit$1.apply(Execute.scala:226)
08:27:48.493 	at sbt.ConcurrentRestrictions$$anon$4$$anonfun$1.apply(ConcurrentRestrictions.scala:159)
08:27:48.493 	at sbt.CompletionService$$anon$2.call(CompletionService.scala:28)
08:27:48.493 	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
08:27:48.493 	at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
08:27:48.493 	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
08:27:48.493 	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1142)
08:27:48.493 	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:617)
08:27:48.493 	at java.lang.Thread.run(Thread.java:745)
08:27:48.493 [0m[[31merror[0m] [0m(*:[31mtexttestRun[0m) There were test failures[0m
08:27:48.499 [0m[[31merror[0m] [0mTotal time: 565 s, completed Jul 13, 2016 8:27:48 AM[0m
08:27:48.565 [go] Current job status: failed.

08:27:48.565 [go] Start to execute task: <exec command="/home/go/.local/bin/xunit_summary" workingdir="ct-t" >
<arg>target/sandbox</arg>
</exec>.
08:27:49.262 FAILURE: stdout different(+) in ct.small.IE01.COMPANY13.COMPANY13
08:27:49.262 Found 13 tests. 1 failures. 0 errors.
08:27:49.370 [go] Current job status: failed.

08:27:49.370 [go] Start to execute task: <exec command="/home/go/.local/bin/link_service_logs" workingdir="ct-t" />.
08:27:49.865 everything under /var/log/services now readable
08:27:50.087 [go] Current job status: failed.

08:27:50.090 [go] Start to create properties ct-t/2064/runTests/1/defaultJob on build-go-agent012 [/var/lib/go-agent]
08:27:50.090 [go] Start to upload ct-t/2064/runTests/1/defaultJob on build-go-agent012 [/var/lib/go-agent]
08:27:50.090 [go] The Directory pipelines/ct-t/ct-t/target/texttest_results specified as a test artifact was not found. Please check your configuration
08:27:50.315 [go] Uploading artifacts from /var/lib/go-agent/pipelines/ct-t/ct-t/target/sandbox/characterize.13Jul082530.16941 to [defaultRoot]
08:27:50.954 [go] Uploading artifacts from /var/lib/go-agent/pipelines/ct-t/ct-t/target/var_log_services to log
08:27:51.151 [go] Uploading artifacts from /tmp/cruise-8f0ae47f-4ec8-475e-86b9-c43ef605a150/c6127750-6d9c-408b-884d-89619aabf9e8/result/index.html to testoutput
08:27:51.156 [go] Uploading artifacts from /tmp/cruise-8f0ae47f-4ec8-475e-86b9-c43ef605a150/c6127750-6d9c-408b-884d-89619aabf9e8/result to testoutput
08:27:51.985 [go] Job completed ct-t/2064/runTests/1/defaultJob on build-go-agent012 [/var/lib/go-agent]
"""


class TestConsoleFetcher(unittest.TestCase):
    def test_console_fetcher_parse_test_index(self):
        error_dictionary = {' COMPANY13': [
            (13, 'new', 'internalxml_IE01-5987313'),
            (13, 'missing', 'documentMetadata4163489'),
            (13, 'missing', 'internalxml_IE01-4163489'),
            (13, 'missing', 'primarypres4163489'),
            (13, 'missing', 'target_fatturapa_1_1_4163489'),
            (13, 'differences', 'catalogue'),
            (13, 'differences', 'routingLog'),
            (13, 'differences', 'stdout')
        ]}
        characterize_console_parser.go_request_console_log = MagicMock(return_value=console_log)
        characterize_console_parser.go_request_junit_report = MagicMock(return_value=(False, ''))
        test_object = characterize_console_parser.TexttestConsoleParser('ct-t', 2064, 1, 'runTests', 'defaultJob')
        output_dictionary = test_object.parse_info()
        self.maxDiff = None
        self.assertEqual(output_dictionary, error_dictionary)


if __name__ == '__main__':
    unittest.main()
