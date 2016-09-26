import unittest
from unittest.mock import MagicMock

from gocddash.console_parsers import git_history_comparison

# noinspection PyPep8
git_history_html = """<!DOCTYPE HTML>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>
    Compare Pipelines Page - Go
</title>

<link debug="false" href="/go/assets/application-a4883f8829c786a9ac744ef3e7261e87210209fd708426d9c042622b549feab9.css" media="all" rel="stylesheet" />
<link debug="false" href="/go/assets/patterns/application-6348f0a8b1b1b32e15371ea7fb2c6d108ef02d953359fe7d83fa4e6a0f8ec8c2.css" media="all" rel="stylesheet" />

<script debug="false" src="/go/assets/application-1c3052b5a6a5a931f22b19dc4fca679c4d802763ebb89df8d3d28f4c5bc1a268.js"></script>
<![if !IE]>
    <script src="/go/assets/lib/d3-3.1.5.min-a8bc188bf658d35d44f7dfc030984253b60843821bffa82b54edd65740c8174b.js"></script>
<![endif]>
<!--[if gt IE 8]><!-->
    <script src="/go/assets/lib/d3-3.1.5.min-a8bc188bf658d35d44f7dfc030984253b60843821bffa82b54edd65740c8174b.js"></script>
<!--<![endif]-->


<link rel="shortcut icon" href="/go/assets/cruise-1592088ba651470e554a54371b6be6b1336462c2186e74fb24f54f177377b538.ico"/>
</head>
<body id="comparison" class="comparison">
<div id="body_bg">
    <div id="header">
        <div class="header clear_float">
  <a href="/go/pipelines" id="application_logo">&nbsp;</a>
  <div class="application_nav">
  <input id="server_timestamp" name="server_time" type="hidden" value="1471509939" />        <ul class="user">
          <li class="help">
            <a href="https://go.cd/help" target="_blank">Need Help?</a>
          </li>
            <li class="current_user icon">
                <a href="#" class="current_user_name dropdown-arrow-icon">name</a>
                <ul class='enhanced_dropdown hidden'>
                    <li>
                        <a href="/go/tab/mycruise/user">Preferences</a>
                    </li>
                    <li class="logout">
                        <a class="sign_out" href="/go/auth/logout" id="nav-logout">Sign out</a>
                    </li>
                </ul>
            </li>
        </ul>


    <ul class="tabs">
        <li id='cruise-header-tab-pipelines' class="">
            <a href="/go/pipelines">PIPELINES</a>        </li>
        <li id='cruise-header-tab-environments' class="">
            <a href="/go/environments">ENVIRONMENTS</a>        </li>
        <li id='cruise-header-tab-agents' class="">
            <a href="/go/agents">AGENTS</a>        </li>
        <li id="cruise-header-tab-admin" class="">
                <a class="dropdown-arrow-icon" data-toggle="dropdown" href="#">ADMIN</a>                <ul class="dropdown-menu" role="menu">
                        <li role="presentation">
    <a href="/go/admin/pipelines">Pipelines</a></li>
<li role="presentation">
    <a href="/go/admin/pipelines/snippet">Config XML</a></li>
<li role="presentation">
    <a href="/go/admin/plugins">Plugins</a></li>
<li role="presentation">
    <a href="/go/admin/package_repositories/new">Package Repositories</a></li>
                </ul>
        </li>
    </ul>
    <div class="error_messaging_counter">
  <div id="cruise_message_counts" class="cruise_messages">
  </div>
  <div id="cruise_message_body" style="display:none;" class="cruise_message_body">
  </div>

     <script type="text/javascript">
        Util.on_load(function() {
          new AjaxRefresher('/go/server/messages.json', null, {
            executeImmediately: true,
            afterRefresh: function(){
              jQuery(document).trigger("server-health-messages-refresh-completed");
            }
          });
        });
     </script>
</div>

</div>
<div id="back_to_top" class='back_to_top' title="Scroll to Top">Top</div>

</div>
    </div>

    <div id='body_content'>
        <div class="messaging_wrapper" id="messaging_wrapper">
            <div class="flash" id="message_pane">
</div>

        </div>
        <div id="pipeline_header">
            <div class="entity_status_wrapper page_header">
                <ul class="entity_title">
    <!--<li><a href="/go/pipelines">Pipelines</a></li>-->
    <li class="name"><a href="/go/tab/pipeline/history/big_repository">big_repository</a></li>

         <li class="last"><h1>Compare</h1> </li>

</ul>
            </div>
        </div>
        <div class="content_wrapper_outer"><div class="content_wrapper_inner">
        <div id="pipeline_status_bar" class="pipeline_flow">
            <table>
                <tbody>
                    <tr>
                        <td width="360px" valign="top"><div class="compare_pipeline_page pipeline">
    <div class="current_instance" id='compare_pipeline_from'>
        <input class="compare_pipeline_input" id="from_pipeline" name="from_pipeline" type="text" value="827" />        <div class="autocomplete"></div>
        <div class="enhanced_dropdown from hidden">
            <div class="compare_search_instructions">
                <p>Search for a pipeline instance by label, commiter, date, etc.</p>
                <p>or</p>
                <p><a class="more_pipelines" id="browse_timeline_link_from">
                    Browse the timeline
                 </a></p>
            </div>
        </div>
    </div>
        <div class="selected_pipeline_from stages">
            <div class="pipeline_details">

    <div style='width: 48.0%' class="stage">
        <div class="stage_bar_wrapper">
                <a href="/go/pipelines/big_repository/827/build/1">
                    <div  class="stage_bar Passed" title="build (Passed)">

                    </div>
                </a>
        </div>
    </div>

    <div style='width: 48.0%' class="stage">
        <div class="stage_bar_wrapper">
                <a href="/go/pipelines/big_repository/827/test/2">
                    <div  class="stage_bar Failed" title="test (Failed)">

                    </div>
                </a>
        </div>
    </div>
<div class="triggered_by">
    <span class='label'>Automatically triggered</span>&nbsp;on&nbsp;<span class='time'>18 Aug, 2016 at 08:45:17 [+0200]</span></div>
            </div>
        </div>
</div>

<script type="text/javascript">
    Util.on_load(function() {
        var pipelineSelector = "#from_pipeline";
        jQuery(pipelineSelector).autocomplete("/go/compare/big_repository/list/compare_with/817", {
            minChars: 1,
            width: 500,
            scrollHeight: 500,
            matchContains: "word",
            selectFirst: false,
            autoFill: false,
            delay: 1000,
            cacheLength: 0,
            multiClickTrigger: false,
            formatItem: function(row, i, max) {
                return row;
            },
            formatMatch: function(row, i, max) {
                return "";
            },
            formatResult: function(row) {
                return row.value;
            },
            parse: function(data) {
                return data.html;
            },
            dataType: 'json',
            highlight: function(value, term) {
                return value;//no-op
            }
        });
        jQuery(pipelineSelector).result(function(event, data, formatted) {
            var dest = compare_path("from", formatted, "817");
            if (formatted == -1) { // indicates no match, see list.json.erb
                resetField(event.target);
            } else {
                window.location.href = dest;
            }
        });
        jQuery(pipelineSelector).blur(function(event) {
            var val = jQuery.trim(jQuery(event.target).val());
            if (val == "" || val != '827') {
                resetField(event.target);
            }
        });
        function resetField(field) {
            jQuery(field).val('827');
        }

        ;
        function compare_path(suffix, counter, fixed_counter) {
            if (suffix == "from") {
                var from_counter = counter;
                var to_counter = fixed_counter;
            } else {
                var from_counter = fixed_counter;
                var to_counter = counter;
            }
            return "/go/compare/big_repository/" + from_counter + "/with/" + to_counter;
        }

        var instructionsPopup = new MicroContentPopup(jQuery('.enhanced_dropdown.from').get(0), new MicroContentPopup.NoOpHandler());
        var instructionsPopupShower = new MicroContentPopup.ClickShower(instructionsPopup);
        jQuery(pipelineSelector).bind('keypress', function(event){
            instructionsPopupShower.close();
        });
        instructionsPopupShower.bindShowButton( jQuery(pipelineSelector).get(0));

        jQuery("#browse_timeline_link_from").click(function(event) {
           Modalbox.show('/go/compare/big_repository/timeline/1?other_pipeline_counter=817&amp;suffix=from',
                {
                    overlayClose: false,
                    title: "Select a pipeline to compare"
                });
        });
    });
</script></td>
                        <td valign="top"><div class="compared_to">compared to</div></td>
                        <td width="360px" valign="top"><div class="compare_pipeline_page pipeline">
    <div class="current_instance" id='compare_pipeline_to'>
        <input class="compare_pipeline_input" id="to_pipeline" name="to_pipeline" type="text" value="817" />        <div class="autocomplete"></div>
        <div class="enhanced_dropdown to hidden">
            <div class="compare_search_instructions">
                <p>Search for a pipeline instance by label, commiter, date, etc.</p>
                <p>or</p>
                <p><a class="more_pipelines" id="browse_timeline_link_to">
                    Browse the timeline
                 </a></p>
            </div>
        </div>
    </div>
        <div class="selected_pipeline_to stages">
            <div class="pipeline_details">

    <div style='width: 48.0%' class="stage">
        <div class="stage_bar_wrapper">
                <a href="/go/pipelines/big_repository/817/build/1">
                    <div  class="stage_bar Passed" title="build (Passed)">

                    </div>
                </a>
        </div>
    </div>

    <div style='width: 48.0%' class="stage">
        <div class="stage_bar_wrapper">
                <a href="/go/pipelines/big_repository/817/test/1">
                    <div  class="stage_bar Passed" title="test (Passed)">

                    </div>
                </a>
        </div>
    </div>
<div class="triggered_by">
    <span class='label'>Automatically triggered</span>&nbsp;on&nbsp;<span class='time'>16 Aug, 2016 at 13:59:34 [+0200]</span></div>
            </div>
        </div>
</div>

<script type="text/javascript">
    Util.on_load(function() {
        var pipelineSelector = "#to_pipeline";
        jQuery(pipelineSelector).autocomplete("/go/compare/big_repository/list/compare_with/827", {
            minChars: 1,
            width: 500,
            scrollHeight: 500,
            matchContains: "word",
            selectFirst: false,
            autoFill: false,
            delay: 1000,
            cacheLength: 0,
            multiClickTrigger: false,
            formatItem: function(row, i, max) {
                return row;
            },
            formatMatch: function(row, i, max) {
                return "";
            },
            formatResult: function(row) {
                return row.value;
            },
            parse: function(data) {
                return data.html;
            },
            dataType: 'json',
            highlight: function(value, term) {
                return value;//no-op
            }
        });
        jQuery(pipelineSelector).result(function(event, data, formatted) {
            var dest = compare_path("to", formatted, "827");
            if (formatted == -1) { // indicates no match, see list.json.erb
                resetField(event.target);
            } else {
                window.location.href = dest;
            }
        });
        jQuery(pipelineSelector).blur(function(event) {
            var val = jQuery.trim(jQuery(event.target).val());
            if (val == "" || val != '817') {
                resetField(event.target);
            }
        });
        function resetField(field) {
            jQuery(field).val('817');
        }

        ;
        function compare_path(suffix, counter, fixed_counter) {
            if (suffix == "from") {
                var from_counter = counter;
                var to_counter = fixed_counter;
            } else {
                var from_counter = fixed_counter;
                var to_counter = counter;
            }
            return "/go/compare/big_repository/" + from_counter + "/with/" + to_counter;
        }

        var instructionsPopup = new MicroContentPopup(jQuery('.enhanced_dropdown.to').get(0), new MicroContentPopup.NoOpHandler());
        var instructionsPopupShower = new MicroContentPopup.ClickShower(instructionsPopup);
        jQuery(pipelineSelector).bind('keypress', function(event){
            instructionsPopupShower.close();
        });
        instructionsPopupShower.bindShowButton( jQuery(pipelineSelector).get(0));

        jQuery("#browse_timeline_link_to").click(function(event) {
           Modalbox.show('/go/compare/big_repository/timeline/1?other_pipeline_counter=827&amp;suffix=to',
                {
                    overlayClose: false,
                    title: "Select a pipeline to compare"
                });
        });
    });
</script></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <script src="/go/gadgets/js/rpc.js?v=1.1-beta5" type="text/javascript"></script>
<script type="text/javascript">
    Util.on_load(function() {
        tw_gadget.init('/go/gadgets/ifr');
    });
</script>
<div class="clear-float"></div>
<div class="sub_tab_container rounded-corner-for-tab-container">
    <div class="sub_tabs_container">
        <ul>
            <li class="checkins current_tab">
                <a class="tab_button_body_match_text">checkins</a>
                <a>Changes</a>
            </li>
            <li class="card_activity">
                <a class="tab_button_body_match_text">card_activity</a>
                <a>Card Activity</a>
            </li>
        </ul>
    </div>
    <div class="sub_tab_container_content">
        <div id="tab-content-of-card_activity">
                        <div id="card_activity_gadget" class="gadget-container">
                    <div class="information">No mingle project configured for this pipeline. <a href="http://www.go.cd/documentation/user/current/integration/mingle_card_activity_gadget.html" target="_blank">More Information</a></div>
                <!-- gadget goes here -->
            </div>
        </div>
        <div id="tab-content-of-checkins" class="material_revision_diff">
                        <div style="padding: 1em;">

        <div>
    <div class="material_title">
        <strong> Git - URL: ssh://git@git/testonline/services/big_repository/app_server.git, Branch: master</strong>
    </div>
    <table class="list_table material_modifications">
        <tr>
            <th class="revision">Revision</th>
            <th class="modified_by">Modified by</th>
            <th class="comment">Comment: </th>
        </tr>
            <tr class="change">
                <td class="revision wrapped_word">
                    efe8f8d9a2e5aa87398e2d338246fd8e950df60d
                </td>
                <td class="modified_by">
                    <span class="wrapped_word"> ab &lt;ab@test.com&gt;</span>
                    <br/>
                    <span class="wrapped_word"> 2016-08-17T15:55:37+02:00</span>
                </td>
                <td class="comment">
                        <p><a href="https://test.atlassian.net" target="story_tracker"></a>testing</p>                </td>
            </tr>
    </table>

        </div>

        <div>
    <div class="material_title">
        <strong> Git - URL: ssh://git@git/testonline/services/big_repository/big_repository.git, Branch: master</strong>
    </div>
    <table class="list_table material_modifications">
        <tr>
            <th class="revision">Revision</th>
            <th class="modified_by">Modified by</th>
            <th class="comment">Comment: </th>
        </tr>
            <tr class="change">
                <td class="revision wrapped_word">
                    9ca18056f017b5869bef325e8f30fa3c2b9c7198
                </td>
                <td class="modified_by">
                    <span class="wrapped_word"> lg &lt;lg@test.com&gt;</span>
                    <br/>
                    <span class="wrapped_word"> 2016-08-18T08:39:43+02:00</span>
                </td>
                <td class="comment">
                        <p>asdf</p>                </td>
            </tr>
            <tr class="change">
                <td class="revision wrapped_word">
                    6ec66540aa09abfda527630d8ab0ecfa651c11d2
                </td>
                <td class="modified_by">
                    <span class="wrapped_word"> rm &lt;rm@test.com&gt;</span>
                    <br/>
                    <span class="wrapped_word"> 2016-08-18T08:27:41+02:00</span>
                </td>
                <td class="comment">
                        <p>qwerty</p>                </td>
            </tr>
            <tr class="change">
                <td class="revision wrapped_word">
                    f493dfcf50591e6efdd7578e461f977699cde1c2
                </td>
                <td class="modified_by">
                    <span class="wrapped_word"> ab &lt;ab@test.com&gt;</span>
                    <br/>
                    <span class="wrapped_word"> 2016-08-17T17:35:51+02:00</span>
                </td>
                <td class="comment">
                        <p><a href="https://test.atlassian.net/" target="story_tracker"></a>hello</p>                </td>
            </tr>
            <tr class="change">
                <td class="revision wrapped_word">
                    1bfdd417c37dd04d356fe1f6e75113afbdc300f5
                </td>
                <td class="modified_by">
                    <span class="wrapped_word"> eb &lt;eb@test.com&gt;</span>
                    <br/>
                    <span class="wrapped_word"> 2016-08-17T16:44:42+02:00</span>
                </td>
                <td class="comment">
                        <p>debug</p>                </td>
            </tr>
            <tr class="change">
                <td class="revision wrapped_word">
                    e8f4dc265be0d0d20f9ad2f9fd74978d1d5ea07e
                </td>
                <td class="modified_by">
                    <span class="wrapped_word"> lg &lt;lg@test.com&gt;</span>
                    <br/>
                    <span class="wrapped_word"> 2016-08-17T16:33:41+02:00</span>
                </td>
                <td class="comment">
                        <p>ids</p>                </td>
            </tr>
            <tr class="change">
                <td class="revision wrapped_word">
                    ba7b91b6d45960e9130096139974a0a0f4cd2df2
                </td>
                <td class="modified_by">
                    <span class="wrapped_word"> go-agent &lt;go-agent@test.com&gt;</span>
                    <br/>
                    <span class="wrapped_word"> 2016-08-17T16:25:12+02:00</span>
                </td>
                <td class="comment">
                        <p>gomongo</p>                </td>
            </tr>
            <tr class="change">
                <td class="revision wrapped_word">
                    32df04538efe309e3ea245fdcedd12e1c6ad773b
                </td>
                <td class="modified_by">
                    <span class="wrapped_word"> ja &lt;ja@test.com&gt;</span>
                    <br/>
                    <span class="wrapped_word"> 2016-08-17T15:31:38+02:00</span>
                </td>
                <td class="comment">
                        <p><a href="https://test.atlassian.net/" target="story_tracker">cherry </a>pick</p>                </td>
            </tr>
            <tr class="change">
                <td class="revision wrapped_word">
                    944004c49589b276603d983871d1a531e9933837
                </td>
                <td class="modified_by">
                    <span class="wrapped_word"> ja &lt;ja@test.com&gt;</span>
                    <br/>
                    <span class="wrapped_word"> 2016-08-17T15:30:43+02:00</span>
                </td>
                <td class="comment">
                        <p><a href="https://test.atlassian.net/" target="story_tracker"></a>cherry pick again</p>                </td>
            </tr>
            <tr class="change">
                <td class="revision wrapped_word">
                    fb543f0e1f9aeaaa70d6a9bc4bfa748d04093ed3
                </td>
                <td class="modified_by">
                    <span class="wrapped_word"> ja &lt;ja@test.com&gt;</span>
                    <br/>
                    <span class="wrapped_word"> 2016-08-17T13:21:04+02:00</span>
                </td>
                <td class="comment">
                        <p><a href="https://test.atlassian.net/" target="story_tracker">testing</a> stuff</p>                </td>
            </tr>
    </table>

        </div>
        <div>
    <div class="material_title">
    <strong class="wrapped_word"> Pipeline - app_server</strong>
</div>
<table class="list_table dependency_material_modifications">
    <tr>
        <th class="dmr revision">Revision</th>
        <th class="dmr label">Label</th>
        <th class="dmr completed_at">Completed at</th>
    </tr>
        <tr class="change">
            <td class="revision">
                <a href="/go/pipelines/app_server/59/build/1">app_server/59/build/1</a>            </td>
            <td class="label">
                <a href="/go/pipelines/value_stream_map/app_server/59">59</a>            </td>
            <td class="completed_at wrapped_word">
                2016-08-17T15:57:20+02:00            </td>
        </tr>
</table>

        </div>
            </div>
        </div>
    </div>
</div>
<script type="text/javascript">
    new TabsManager(undefined, 'comparison_page', 'big_repository>', 'checkins');
</script>
        </div></div>
    </div>

    <div id='footer-new-foundation'>
      <footer class="footer">
    <div class="row">
        <div class="small-12 medium-6 large-8 columns">
            <p class="copyright">Copyright &copy; 2016
                <a href="https://www.thoughtworks.com/products" target='_blank'>ThoughtWorks, Inc.</a>
                Licensed under <a href="https://www.apache.org/licenses/LICENSE-2.0" target="_blank">Apache License, Version 2.0</a>.<br/>
                Go includes <a href="/go/NOTICE/cruise_notice_file.pdf" target="_blank">third-party software</a>.
                Go Version: 16.7.0 (3819-b0b9921bdea58101121cc181d697355177d2f197).
            </p>

        </div>
      <div class="small-12 medium-6 large-4 columns">
            <span class="inline-list social">
                <a href="https://twitter.com/goforcd" title="twitter" class="twitter"></a>
                <a href="https://github.com/gocd/gocd" title="github" class="github"></a>
                <a href="https://groups.google.com/d/forum/go-cd" title="forums" class="forums"></a>
                <a href="https://docs.go.cd/current" title="documentation" class="documentation"></a>
                <a href="https://www.go.cd/community/plugins.html" title="plugins" class="plugins"></a>
                <a href="https://api.go.cd/current" title="api" class="api"></a>
                <a href="/go/about" title="about" class="server-details"></a>
                <a href="/go/cctray.xml" title="cctray" class="cctray"></a>
            </span>
      </div>
    </div>
</footer>

  <script type="text/javascript">
    var updater = new VersionUpdater('http://go.test.local/go/api/version_infos/stale', 'http://go.test.local/go/api/version_infos/go_server');
    updater.update();
  </script>

    </div>
</div>
</body>
</html>
"""

# noinspection PyPep8
material_revision_diff = """<!DOCTYPE HTML>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>
        Compare Pipelines Page - Go
    </title>

    <link debug="false" href="/go/assets/application-a4883f8829c786a9ac744ef3e7261e87210209fd708426d9c042622b549feab9.css" media="all" rel="stylesheet" />
    <link debug="false" href="/go/assets/patterns/application-6348f0a8b1b1b32e15371ea7fb2c6d108ef02d953359fe7d83fa4e6a0f8ec8c2.css" media="all" rel="stylesheet" />

    <script debug="false" src="/go/assets/application-1c3052b5a6a5a931f22b19dc4fca679c4d802763ebb89df8d3d28f4c5bc1a268.js"></script>
    <![if !IE]>
    <script src="/go/assets/lib/d3-3.1.5.min-a8bc188bf658d35d44f7dfc030984253b60843821bffa82b54edd65740c8174b.js"></script>
    <![endif]>
    <!--[if gt IE 8]><!-->
    <script src="/go/assets/lib/d3-3.1.5.min-a8bc188bf658d35d44f7dfc030984253b60843821bffa82b54edd65740c8174b.js"></script>
    <!--<![endif]-->


    <link rel="shortcut icon" href="/go/assets/cruise-1592088ba651470e554a54371b6be6b1336462c2186e74fb24f54f177377b538.ico"/>
</head>
<body id="comparison" class="comparison">
<div id="body_bg">
    <div id="header">
        <div class="header clear_float">
            <a href="/go/pipelines" id="application_logo">&nbsp;</a>
            <div class="application_nav">
                <input id="server_timestamp" name="server_time" type="hidden" value="1471509939" />        <ul class="user">
                <li class="help">
                    <a href="https://go.cd/help" target="_blank">Need Help?</a>
                </li>
                <li class="current_user icon">
                    <a href="#" class="current_user_name dropdown-arrow-icon">name</a>
                    <ul class='enhanced_dropdown hidden'>
                        <li>
                            <a href="/go/tab/mycruise/user">Preferences</a>
                        </li>
                        <li class="logout">
                            <a class="sign_out" href="/go/auth/logout" id="nav-logout">Sign out</a>
                        </li>
                    </ul>
                </li>
            </ul>


                <ul class="tabs">
                    <li id='cruise-header-tab-pipelines' class="">
                        <a href="/go/pipelines">PIPELINES</a>        </li>
                    <li id='cruise-header-tab-environments' class="">
                        <a href="/go/environments">ENVIRONMENTS</a>        </li>
                    <li id='cruise-header-tab-agents' class="">
                        <a href="/go/agents">AGENTS</a>        </li>
                    <li id="cruise-header-tab-admin" class="">
                        <a class="dropdown-arrow-icon" data-toggle="dropdown" href="#">ADMIN</a>                <ul class="dropdown-menu" role="menu">
                        <li role="presentation">
                            <a href="/go/admin/pipelines">Pipelines</a></li>
                        <li role="presentation">
                            <a href="/go/admin/pipelines/snippet">Config XML</a></li>
                        <li role="presentation">
                            <a href="/go/admin/plugins">Plugins</a></li>
                        <li role="presentation">
                            <a href="/go/admin/package_repositories/new">Package Repositories</a></li>
                    </ul>
                    </li>
                </ul>
                <div class="error_messaging_counter">
                    <div id="cruise_message_counts" class="cruise_messages">
                    </div>
                    <div id="cruise_message_body" style="display:none;" class="cruise_message_body">
                    </div>

                    <script type="text/javascript">
                        Util.on_load(function() {
                            new AjaxRefresher('/go/server/messages.json', null, {
                                executeImmediately: true,
                                afterRefresh: function(){
                                    jQuery(document).trigger("server-health-messages-refresh-completed");
                                }
                            });
                        });
                    </script>
                </div>

            </div>
            <div id="back_to_top" class='back_to_top' title="Scroll to Top">Top</div>

        </div>
    </div>

    <div id='body_content'>
        <div class="messaging_wrapper" id="messaging_wrapper">
            <div class="flash" id="message_pane">
            </div>

        </div>
        <div id="pipeline_header">
            <div class="entity_status_wrapper page_header">
                <ul class="entity_title">
                    <!--<li><a href="/go/pipelines">Pipelines</a></li>-->
                    <li class="name"><a href="/go/tab/pipeline/history/big_repository">big_repository</a></li>

                    <li class="last"><h1>Compare</h1> </li>

                </ul>
            </div>
        </div>
        <div class="content_wrapper_outer"><div class="content_wrapper_inner">
            <div id="pipeline_status_bar" class="pipeline_flow">
                <table>
                    <tbody>
                    <tr>
                        <td width="360px" valign="top"><div class="compare_pipeline_page pipeline">
                            <div class="current_instance" id='compare_pipeline_from'>
                                <input class="compare_pipeline_input" id="from_pipeline" name="from_pipeline" type="text" value="827" />        <div class="autocomplete"></div>
                                <div class="enhanced_dropdown from hidden">
                                    <div class="compare_search_instructions">
                                        <p>Search for a pipeline instance by label, commiter, date, etc.</p>
                                        <p>or</p>
                                        <p><a class="more_pipelines" id="browse_timeline_link_from">
                                            Browse the timeline
                                        </a></p>
                                    </div>
                                </div>
                            </div>
                            <div class="selected_pipeline_from stages">
                                <div class="pipeline_details">

                                    <div style='width: 48.0%' class="stage">
                                        <div class="stage_bar_wrapper">
                                            <a href="/go/pipelines/big_repository/827/build/1">
                                                <div  class="stage_bar Passed" title="build (Passed)">

                                                </div>
                                            </a>
                                        </div>
                                    </div>

                                    <div style='width: 48.0%' class="stage">
                                        <div class="stage_bar_wrapper">
                                            <a href="/go/pipelines/big_repository/827/test/2">
                                                <div  class="stage_bar Failed" title="test (Failed)">

                                                </div>
                                            </a>
                                        </div>
                                    </div>
                                    <div class="triggered_by">
                                        <span class='label'>Automatically triggered</span>&nbsp;on&nbsp;<span class='time'>18 Aug, 2016 at 08:45:17 [+0200]</span></div>
                                </div>
                            </div>
                        </div>

                            <script type="text/javascript">
                                Util.on_load(function() {
                                    var pipelineSelector = "#from_pipeline";
                                    jQuery(pipelineSelector).autocomplete("/go/compare/big_repository/list/compare_with/817", {
                                        minChars: 1,
                                        width: 500,
                                        scrollHeight: 500,
                                        matchContains: "word",
                                        selectFirst: false,
                                        autoFill: false,
                                        delay: 1000,
                                        cacheLength: 0,
                                        multiClickTrigger: false,
                                        formatItem: function(row, i, max) {
                                            return row;
                                        },
                                        formatMatch: function(row, i, max) {
                                            return "";
                                        },
                                        formatResult: function(row) {
                                            return row.value;
                                        },
                                        parse: function(data) {
                                            return data.html;
                                        },
                                        dataType: 'json',
                                        highlight: function(value, term) {
                                            return value;//no-op
                                        }
                                    });
                                    jQuery(pipelineSelector).result(function(event, data, formatted) {
                                        var dest = compare_path("from", formatted, "817");
                                        if (formatted == -1) { // indicates no match, see list.json.erb
                                            resetField(event.target);
                                        } else {
                                            window.location.href = dest;
                                        }
                                    });
                                    jQuery(pipelineSelector).blur(function(event) {
                                        var val = jQuery.trim(jQuery(event.target).val());
                                        if (val == "" || val != '827') {
                                            resetField(event.target);
                                        }
                                    });
                                    function resetField(field) {
                                        jQuery(field).val('827');
                                    }

                                    ;
                                    function compare_path(suffix, counter, fixed_counter) {
                                        if (suffix == "from") {
                                            var from_counter = counter;
                                            var to_counter = fixed_counter;
                                        } else {
                                            var from_counter = fixed_counter;
                                            var to_counter = counter;
                                        }
                                        return "/go/compare/big_repository/" + from_counter + "/with/" + to_counter;
                                    }

                                    var instructionsPopup = new MicroContentPopup(jQuery('.enhanced_dropdown.from').get(0), new MicroContentPopup.NoOpHandler());
                                    var instructionsPopupShower = new MicroContentPopup.ClickShower(instructionsPopup);
                                    jQuery(pipelineSelector).bind('keypress', function(event){
                                        instructionsPopupShower.close();
                                    });
                                    instructionsPopupShower.bindShowButton( jQuery(pipelineSelector).get(0));

                                    jQuery("#browse_timeline_link_from").click(function(event) {
                                        Modalbox.show('/go/compare/big_repository/timeline/1?other_pipeline_counter=817&amp;suffix=from',
                                                {
                                                    overlayClose: false,
                                                    title: "Select a pipeline to compare"
                                                });
                                    });
                                });
                            </script></td>
                        <td valign="top"><div class="compared_to">compared to</div></td>
                        <td width="360px" valign="top"><div class="compare_pipeline_page pipeline">
                            <div class="current_instance" id='compare_pipeline_to'>
                                <input class="compare_pipeline_input" id="to_pipeline" name="to_pipeline" type="text" value="817" />        <div class="autocomplete"></div>
                                <div class="enhanced_dropdown to hidden">
                                    <div class="compare_search_instructions">
                                        <p>Search for a pipeline instance by label, commiter, date, etc.</p>
                                        <p>or</p>
                                        <p><a class="more_pipelines" id="browse_timeline_link_to">
                                            Browse the timeline
                                        </a></p>
                                    </div>
                                </div>
                            </div>
                            <div class="selected_pipeline_to stages">
                                <div class="pipeline_details">

                                    <div style='width: 48.0%' class="stage">
                                        <div class="stage_bar_wrapper">
                                            <a href="/go/pipelines/big_repository/817/build/1">
                                                <div  class="stage_bar Passed" title="build (Passed)">

                                                </div>
                                            </a>
                                        </div>
                                    </div>

                                    <div style='width: 48.0%' class="stage">
                                        <div class="stage_bar_wrapper">
                                            <a href="/go/pipelines/big_repository/817/test/1">
                                                <div  class="stage_bar Passed" title="test (Passed)">

                                                </div>
                                            </a>
                                        </div>
                                    </div>
                                    <div class="triggered_by">
                                        <span class='label'>Automatically triggered</span>&nbsp;on&nbsp;<span class='time'>16 Aug, 2016 at 13:59:34 [+0200]</span></div>
                                </div>
                            </div>
                        </div>

                            <script type="text/javascript">
                                Util.on_load(function() {
                                    var pipelineSelector = "#to_pipeline";
                                    jQuery(pipelineSelector).autocomplete("/go/compare/big_repository/list/compare_with/827", {
                                        minChars: 1,
                                        width: 500,
                                        scrollHeight: 500,
                                        matchContains: "word",
                                        selectFirst: false,
                                        autoFill: false,
                                        delay: 1000,
                                        cacheLength: 0,
                                        multiClickTrigger: false,
                                        formatItem: function(row, i, max) {
                                            return row;
                                        },
                                        formatMatch: function(row, i, max) {
                                            return "";
                                        },
                                        formatResult: function(row) {
                                            return row.value;
                                        },
                                        parse: function(data) {
                                            return data.html;
                                        },
                                        dataType: 'json',
                                        highlight: function(value, term) {
                                            return value;//no-op
                                        }
                                    });
                                    jQuery(pipelineSelector).result(function(event, data, formatted) {
                                        var dest = compare_path("to", formatted, "827");
                                        if (formatted == -1) { // indicates no match, see list.json.erb
                                            resetField(event.target);
                                        } else {
                                            window.location.href = dest;
                                        }
                                    });
                                    jQuery(pipelineSelector).blur(function(event) {
                                        var val = jQuery.trim(jQuery(event.target).val());
                                        if (val == "" || val != '817') {
                                            resetField(event.target);
                                        }
                                    });
                                    function resetField(field) {
                                        jQuery(field).val('817');
                                    }

                                    ;
                                    function compare_path(suffix, counter, fixed_counter) {
                                        if (suffix == "from") {
                                            var from_counter = counter;
                                            var to_counter = fixed_counter;
                                        } else {
                                            var from_counter = fixed_counter;
                                            var to_counter = counter;
                                        }
                                        return "/go/compare/big_repository/" + from_counter + "/with/" + to_counter;
                                    }

                                    var instructionsPopup = new MicroContentPopup(jQuery('.enhanced_dropdown.to').get(0), new MicroContentPopup.NoOpHandler());
                                    var instructionsPopupShower = new MicroContentPopup.ClickShower(instructionsPopup);
                                    jQuery(pipelineSelector).bind('keypress', function(event){
                                        instructionsPopupShower.close();
                                    });
                                    instructionsPopupShower.bindShowButton( jQuery(pipelineSelector).get(0));

                                    jQuery("#browse_timeline_link_to").click(function(event) {
                                        Modalbox.show('/go/compare/big_repository/timeline/1?other_pipeline_counter=827&amp;suffix=to',
                                                {
                                                    overlayClose: false,
                                                    title: "Select a pipeline to compare"
                                                });
                                    });
                                });
                            </script></td>
                    </tr>
                    </tbody>
                </table>
            </div>

            <script src="/go/gadgets/js/rpc.js?v=1.1-beta5" type="text/javascript"></script>
            <script type="text/javascript">
                Util.on_load(function() {
                    tw_gadget.init('/go/gadgets/ifr');
                });
            </script>
            <div class="clear-float"></div>
            <div class="sub_tab_container rounded-corner-for-tab-container">
                <div class="sub_tabs_container">
                    <ul>
                        <li class="checkins current_tab">
                            <a class="tab_button_body_match_text">checkins</a>
                            <a>Changes</a>
                        </li>
                        <li class="card_activity">
                            <a class="tab_button_body_match_text">card_activity</a>
                            <a>Card Activity</a>
                        </li>
                    </ul>
                </div>
                <div class="sub_tab_container_content">
                    <div id="tab-content-of-card_activity">
                        <div class="information">
                            <div class="message">
                <span>
                    This comparison involves a pipeline instance that was triggered with a non-sequential material revision.                </span>
                <span class="prompt">
                    <a class="link_as_header_button"
                       href="/go/compare/paysol/800/with/817?show_bisect=true">Continue</a>                </span>
                            </div>
                        </div>


                        <div id="card_activity_gadget" class="gadget-container">
                            <div class="information">No mingle project configured for this pipeline. <a
                                    href="http://www.go.cd/documentation/user/current/integration/mingle_card_activity_gadget.html"
                                    target="_blank">More Information</a></div>
                            <!-- gadget goes here -->
                        </div>
                    </div>
                    <div id="tab-content-of-checkins" class="material_revision_diff">
                        <div style="padding: 1em;">

                            <div>
                                <div class="material_title">
                                    <strong> Git - URL: ssh://git@git/testonline/services/big_repository/app_server.git, Branch: master</strong>
                                </div>
                                <table class="list_table material_modifications">
                                    <tr>
                                        <th class="revision">Revision</th>
                                        <th class="modified_by">Modified by</th>
                                        <th class="comment">Comment: </th>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision wrapped_word">
                                            efe8f8d9a2e5aa87398e2d338246fd8e950df60d
                                        </td>
                                        <td class="modified_by">
                                            <span class="wrapped_word"> ab &lt;ab@test.com&gt;</span>
                                            <br/>
                                            <span class="wrapped_word"> 2016-08-17T15:55:37+02:00</span>
                                        </td>
                                        <td class="comment">
                                            <p><a href="https://test.atlassian.net" target="story_tracker"></a>testing</p>                </td>
                                    </tr>
                                </table>

                            </div>

                            <div>
                                <div class="material_title">
                                    <strong> Git - URL: ssh://git@git/testonline/services/big_repository/big_repository.git, Branch: master</strong>
                                </div>
                                <table class="list_table material_modifications">
                                    <tr>
                                        <th class="revision">Revision</th>
                                        <th class="modified_by">Modified by</th>
                                        <th class="comment">Comment: </th>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision wrapped_word">
                                            9ca18056f017b5869bef325e8f30fa3c2b9c7198
                                        </td>
                                        <td class="modified_by">
                                            <span class="wrapped_word"> lg &lt;lg@test.com&gt;</span>
                                            <br/>
                                            <span class="wrapped_word"> 2016-08-18T08:39:43+02:00</span>
                                        </td>
                                        <td class="comment">
                                            <p>asdf</p>                </td>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision wrapped_word">
                                            6ec66540aa09abfda527630d8ab0ecfa651c11d2
                                        </td>
                                        <td class="modified_by">
                                            <span class="wrapped_word"> rm &lt;rm@test.com&gt;</span>
                                            <br/>
                                            <span class="wrapped_word"> 2016-08-18T08:27:41+02:00</span>
                                        </td>
                                        <td class="comment">
                                            <p>qwerty</p>                </td>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision wrapped_word">
                                            f493dfcf50591e6efdd7578e461f977699cde1c2
                                        </td>
                                        <td class="modified_by">
                                            <span class="wrapped_word"> ab &lt;ab@test.com&gt;</span>
                                            <br/>
                                            <span class="wrapped_word"> 2016-08-17T17:35:51+02:00</span>
                                        </td>
                                        <td class="comment">
                                            <p><a href="https://test.atlassian.net/" target="story_tracker"></a>hello</p>                </td>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision wrapped_word">
                                            1bfdd417c37dd04d356fe1f6e75113afbdc300f5
                                        </td>
                                        <td class="modified_by">
                                            <span class="wrapped_word"> eb &lt;eb@test.com&gt;</span>
                                            <br/>
                                            <span class="wrapped_word"> 2016-08-17T16:44:42+02:00</span>
                                        </td>
                                        <td class="comment">
                                            <p>debug</p>                </td>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision wrapped_word">
                                            e8f4dc265be0d0d20f9ad2f9fd74978d1d5ea07e
                                        </td>
                                        <td class="modified_by">
                                            <span class="wrapped_word"> lg &lt;lg@test.com&gt;</span>
                                            <br/>
                                            <span class="wrapped_word"> 2016-08-17T16:33:41+02:00</span>
                                        </td>
                                        <td class="comment">
                                            <p>ids</p>                </td>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision wrapped_word">
                                            ba7b91b6d45960e9130096139974a0a0f4cd2df2
                                        </td>
                                        <td class="modified_by">
                                            <span class="wrapped_word"> go-agent &lt;go-agent@test.com&gt;</span>
                                            <br/>
                                            <span class="wrapped_word"> 2016-08-17T16:25:12+02:00</span>
                                        </td>
                                        <td class="comment">
                                            <p>gomongo</p>                </td>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision wrapped_word">
                                            32df04538efe309e3ea245fdcedd12e1c6ad773b
                                        </td>
                                        <td class="modified_by">
                                            <span class="wrapped_word"> ja &lt;ja@test.com&gt;</span>
                                            <br/>
                                            <span class="wrapped_word"> 2016-08-17T15:31:38+02:00</span>
                                        </td>
                                        <td class="comment">
                                            <p><a href="https://test.atlassian.net/" target="story_tracker">cherry </a>pick</p>                </td>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision wrapped_word">
                                            944004c49589b276603d983871d1a531e9933837
                                        </td>
                                        <td class="modified_by">
                                            <span class="wrapped_word"> ja &lt;ja@test.com&gt;</span>
                                            <br/>
                                            <span class="wrapped_word"> 2016-08-17T15:30:43+02:00</span>
                                        </td>
                                        <td class="comment">
                                            <p><a href="https://test.atlassian.net/" target="story_tracker"></a>cherry pick again</p>                </td>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision wrapped_word">
                                            fb543f0e1f9aeaaa70d6a9bc4bfa748d04093ed3
                                        </td>
                                        <td class="modified_by">
                                            <span class="wrapped_word"> ja &lt;ja@test.com&gt;</span>
                                            <br/>
                                            <span class="wrapped_word"> 2016-08-17T13:21:04+02:00</span>
                                        </td>
                                        <td class="comment">
                                            <p><a href="https://test.atlassian.net/" target="story_tracker">testing</a> stuff</p>                </td>
                                    </tr>
                                </table>

                            </div>
                            <div>
                                <div class="material_title">
                                    <strong class="wrapped_word"> Pipeline - app_server</strong>
                                </div>
                                <table class="list_table dependency_material_modifications">
                                    <tr>
                                        <th class="dmr revision">Revision</th>
                                        <th class="dmr label">Label</th>
                                        <th class="dmr completed_at">Completed at</th>
                                    </tr>
                                    <tr class="change">
                                        <td class="revision">
                                            <a href="/go/pipelines/app_server/59/build/1">app_server/59/build/1</a>            </td>
                                        <td class="label">
                                            <a href="/go/pipelines/value_stream_map/app_server/59">59</a>            </td>
                                        <td class="completed_at wrapped_word">
                                            2016-08-17T15:57:20+02:00            </td>
                                    </tr>
                                </table>

                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script type="text/javascript">
                new TabsManager(undefined, 'comparison_page', 'big_repository>', 'checkins');
            </script>
        </div></div>
    </div>

    <div id='footer-new-foundation'>
        <footer class="footer">
            <div class="row">
                <div class="small-12 medium-6 large-8 columns">
                    <p class="copyright">Copyright &copy; 2016
                        <a href="https://www.thoughtworks.com/products" target='_blank'>ThoughtWorks, Inc.</a>
                        Licensed under <a href="https://www.apache.org/licenses/LICENSE-2.0" target="_blank">Apache License, Version 2.0</a>.<br/>
                        Go includes <a href="/go/NOTICE/cruise_notice_file.pdf" target="_blank">third-party software</a>.
                        Go Version: 16.7.0 (3819-b0b9921bdea58101121cc181d697355177d2f197).
                    </p>

                </div>
                <div class="small-12 medium-6 large-4 columns">
            <span class="inline-list social">
                <a href="https://twitter.com/goforcd" title="twitter" class="twitter"></a>
                <a href="https://github.com/gocd/gocd" title="github" class="github"></a>
                <a href="https://groups.google.com/d/forum/go-cd" title="forums" class="forums"></a>
                <a href="https://docs.go.cd/current" title="documentation" class="documentation"></a>
                <a href="https://www.go.cd/community/plugins.html" title="plugins" class="plugins"></a>
                <a href="https://api.go.cd/current" title="api" class="api"></a>
                <a href="/go/about" title="about" class="server-details"></a>
                <a href="/go/cctray.xml" title="cctray" class="cctray"></a>
            </span>
                </div>
            </div>
        </footer>

        <script type="text/javascript">
            var updater = new VersionUpdater('http://go.test.local/go/api/version_infos/stale', 'http://go.test.local/go/api/version_infos/go_server');
            updater.update();
        </script>

    </div>
</div>
</body>
</html>"""


class TestGitBlame(unittest.TestCase):
    def test_git_blame(self):
        pipeline_name = "banana"
        current = "2029"
        comparison = "2029"

        git_history_comparison.go_request_comparison_html = MagicMock(return_value=git_history_html)
        output = git_history_comparison.get_git_comparison(pipeline_name, current, comparison, 'banana')
        self.assertEqual(output, [
            ('app_server.git, Branch: master', [
                ('efe8f8d9a2e5aa87398e2d338246fd8e950df60d', 'ab <ab@test.com> 2016-08-17T15:55:37+02:00', 'testing')
            ]),
            ('big_repository.git, Branch: master', [
                ('9ca18056f017b5869bef325e8f30fa3c2b9c7198', 'lg <lg@test.com> 2016-08-18T08:39:43+02:00', 'asdf'),
                ('6ec66540aa09abfda527630d8ab0ecfa651c11d2', 'rm <rm@test.com> 2016-08-18T08:27:41+02:00', 'qwerty'),
                ('f493dfcf50591e6efdd7578e461f977699cde1c2', 'ab <ab@test.com> 2016-08-17T17:35:51+02:00', 'hello'),
                ('1bfdd417c37dd04d356fe1f6e75113afbdc300f5', 'eb <eb@test.com> 2016-08-17T16:44:42+02:00', 'debug'),
                ('e8f4dc265be0d0d20f9ad2f9fd74978d1d5ea07e', 'lg <lg@test.com> 2016-08-17T16:33:41+02:00', 'ids'),
                ('32df04538efe309e3ea245fdcedd12e1c6ad773b', 'ja <ja@test.com> 2016-08-17T15:31:38+02:00',
                 'cherry pick'),
                ('944004c49589b276603d983871d1a531e9933837', 'ja <ja@test.com> 2016-08-17T15:30:43+02:00',
                 'cherry pick again'),
                ('fb543f0e1f9aeaaa70d6a9bc4bfa748d04093ed3', 'ja <ja@test.com> 2016-08-17T13:21:04+02:00',
                 'testing stuff')
            ])
        ])

    def test_material_revision_diff(self):
        pipeline_name = "banana"
        current = "295"
        comparison = "294"

        git_history_comparison.go_request_comparison_html = MagicMock(return_value=material_revision_diff)
        output = git_history_comparison.get_git_comparison(pipeline_name, current, comparison, 'banana')
        self.assertEqual(output, None)


if __name__ == '__main__':
    unittest.main()
