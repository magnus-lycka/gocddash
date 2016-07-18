import unittest
from unittest.mock import MagicMock

from gocddash.console_parsers import git_blame_compare

git_blame = """
        <div id="pipeline_header">
            <div class="entity_status_wrapper page_header">
                <ul class="entity_title">
    <!--<li><a href="/go/pipelines">Pipelines</a></li>-->
    <li class="name"><a href="/go/tab/pipeline/history/ct-t">ct-t</a></li>

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
        <input class="compare_pipeline_input" id="from_pipeline" name="from_pipeline" type="text" value="2076" />        <div class="autocomplete"></div>
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

    <div style='width: 97.0%' class="stage">
        <div class="stage_bar_wrapper">
                <a href="/go/pipelines/ct-t/2076/runTests/1">
                    <div  class="stage_bar Passed" title="runTests (Passed)">

                    </div>
                </a>
        </div>
    </div>
<div class="triggered_by">
    <span class='label'>Automatically triggered</span>&nbsp;on&nbsp;<span class='time'>14 Jul, 2016 at 06:34:55 [+0200]</span></div>
            </div>
        </div>
</div>
</td>
                        <td valign="top"><div class="compared_to">compared to</div></td>
                        <td width="360px" valign="top"><div class="compare_pipeline_page pipeline">
    <div class="current_instance" id='compare_pipeline_to'>
        <input class="compare_pipeline_input" id="to_pipeline" name="to_pipeline" type="text" value="2076" />        <div class="autocomplete"></div>
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

    <div style='width: 97.0%' class="stage">
        <div class="stage_bar_wrapper">
                <a href="/go/pipelines/ct-t/2076/runTests/1">
                    <div  class="stage_bar Passed" title="runTests (Passed)">

                    </div>
                </a>
        </div>
    </div>
<div class="triggered_by">
    <span class='label'>Automatically triggered</span>&nbsp;on&nbsp;<span class='time'>14 Jul, 2016 at 06:34:55 [+0200]</span></div>
            </div>
        </div>
</div>
</td>
                    </tr>
                </tbody>
            </table>
        </div>

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
        <strong> Git - URL: ssh://git@git/internet/services/banana/banana.git, Branch: master</strong>
    </div>
    <table class="list_table material_modifications">
        <tr>
            <th class="revision">Revision</th>
            <th class="modified_by">Modified by</th>
            <th class="comment">Comment: </th>
        </tr>
            <tr class="change">
                <td class="revision">
                    87cfcf8f4655d8e<wbr/>5f2713636<wbr/>df26820b0cbd0513                </td>
                <td class="modified_by">
                    A B &lt;A.B@asdf.com&gt;                    <br/>
                    2016-<wbr/>07-<wbr/>13T23:28:57+02:<wbr/>00                </td>
                <td class="comment">
                        <p>Grapefruit</p>                </td>
            </tr>
    </table>

        </div>

        <div>
    <div class="material_title">
        <strong> Git - URL: ssh://git@git/internet/services/pineapple/pineapple.git, Branch: master</strong>
    </div>
    <table class="list_table material_modifications">
        <tr>
            <th class="revision">Revision</th>
            <th class="modified_by">Modified by</th>
            <th class="comment">Comment: </th>
        </tr>
            <tr class="change">
                <td class="revision">
                    261d2d6c3f02907<wbr/>29d2a6095<wbr/>2120b4736c6ad1a5                </td>
                <td class="modified_by">
                    X Y &lt;X.Y@asdf.com&gt;                    <br/>
                    2016-<wbr/>07-<wbr/>14T05:31:31+02:<wbr/>00                </td>
                <td class="comment">
                        <p>Pear</p>                </td>
            </tr>
            <tr class="change">
                <td class="revision">
                    a6884dc475e20b8<wbr/>d69fbf588<wbr/>ad4aa9beef4c466e                </td>
                <td class="modified_by">
                    X Y &lt;X.Y@asdf.com&gt;                    <br/>
                    2016-<wbr/>07-<wbr/>13T23:09:02+02:<wbr/>00                </td>
                <td class="comment">
                        <p>Kiwi</p>                </td>
            </tr>
    </table>

        </div>
        <div>
    <div class="material_title">
    <strong> Pipeline - psl</strong>
</div>
<table class="list_table dependency_material_modifications">
    <tr>
        <th class="dmr revision">Revision</th>
        <th class="dmr label">Label</th>
        <th class="dmr completed_at">Completed at</th>
    </tr>
        <tr class="change">
            <td class="revision">
                <a href="/go/pipelines/psl/743/test/1">psl/743/test/1</a>            </td>
            <td class="label">
                <a href="/go/pipelines/value_stream_map/psl/743">743</a>            </td>
            <td class="completed_at">
                2016-<wbr/>07-<wbr/>14T06:31:44+02:<wbr/>00            </td>
        </tr>
</table>

        </div>
        <div>
    <div class="material_title">
    <strong> Pipeline - update-<wbr/>pl</strong>
</div>
<table class="list_table dependency_material_modifications">
    <tr>
        <th class="dmr revision">Revision</th>
        <th class="dmr label">Label</th>
        <th class="dmr completed_at">Completed at</th>
    </tr>
        <tr class="change">
            <td class="revision">
                <a href="/go/pipelines/update-pl/2143/build/1">update-pl/2143/build/1</a>            </td>
            <td class="label">
                <a href="/go/pipelines/value_stream_map/update-pl/2143">2143</a>            </td>
            <td class="completed_at">
                2016-<wbr/>07-<wbr/>14T06:33:59+02:<wbr/>00            </td>
        </tr>
</table>

        </div>
            </div>
        </div>
    </div>
</div>
"""

class TestGitBlame(unittest.TestCase):
    def test_git_blame(self):
        pipeline_name = "banana"
        current = "2029"
        comparison = "2029"

        git_blame_compare.go_request_comparison_html = MagicMock(return_value=git_blame)
        output = git_blame_compare.get_git_comparison(pipeline_name, current, comparison)
        self.assertEqual(output, [
            [u'banana.git', u' Git - URL: ssh://git@git/internet/services/banana/banana.git',
             u'87cfcf8f4655d8e5f2713636df26820b0cbd0513', u'A B <A.B@asdf.com>',
             u'Grapefruit'],
            [u'pineapple.git', u' Git - URL: ssh://git@git/internet/services/pineapple/pineapple.git',
             u'261d2d6c3f0290729d2a60952120b4736c6ad1a5', u'X Y <X.Y@asdf.com>',
             u'Pear'],
            [u'pineapple.git', u' Git - URL: ssh://git@git/internet/services/pineapple/pineapple.git',
             u'a6884dc475e20b8d69fbf588ad4aa9beef4c466e', u'X Y <X.Y@asdf.com>',
             u'Kiwi']])


if __name__ == '__main__':
    unittest.main()
