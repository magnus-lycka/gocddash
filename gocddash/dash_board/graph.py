from collections import OrderedDict

import pandas as pd
from bokeh.charts import Bar
from bokeh.charts.attributes import cat
from bokeh.charts.operations import blend
from bokeh.embed import components
from bokeh.models import GlyphRenderer
from bokeh.models import HoverTool
from bokeh.models import Range1d
from bokeh.plotting import *
from bokeh.resources import INLINE

from gocddash.analysis.data_access import create_connection
from gocddash.analysis.domain import get_graph_statistics, get_graph_statistics_for_final_stages


def show_graph(plot):
    show(plot)


def create_agent_html_graph_deprecated(pipeline_name, title):
    graph_data = get_graph_statistics(pipeline_name)

    result_list = [
        row.job_result.replace("Passed", str(1)) if row.job_result == "Passed" else row.job_result.replace("Failed",
                                                                                                           str(0)) for
        row in graph_data]

    agent_list = [row.agent_name[9:] for row in graph_data]

    panda_frame = pd.DataFrame(columns=['agent_name', 'result', 'number_of_records'])
    panda_frame['agent_name'] = agent_list

    panda_frame['result'] = result_list
    panda_frame['result'] = pd.to_numeric(panda_frame['result'])
    panda_frame = panda_frame.groupby(panda_frame['agent_name']).agg(['mean', 'size']).reset_index()
    panda_frame.columns = ['agent_name', 'result', 'NoR']

    output_file(title + ".html", title=title)
    tools = "hover,previewsave"

    agent_bar_chart = Bar(panda_frame, label='agent_name', values='result', width=500, height=400,
                          legend=None, tools=tools, title=title, agg='mean', color='#2196f3', toolbar_location="above")

    hover = agent_bar_chart.select(dict(type=HoverTool))

    # Manually map Number of Records (NoR) to correct ColumnDataSource
    # See https://github.com/bokeh/bokeh/issues/2965 for details and possible workaround if they update the module
    glyphs = agent_bar_chart.select(GlyphRenderer)
    for item in glyphs:
        panda_index = panda_frame['agent_name'].str.contains(item.data_source.data['agent_name'][0])
        panda_index = panda_index[panda_index == True].index[0]  # Pandas specific syntax. Ignore IDEA warning.
        item.data_source.data['NoR'] = [panda_frame.get_value(index=panda_index, col='NoR')]

    hover.tooltips = OrderedDict([
        ("Success rate", "@height"),
        ("Agent Name", "@agent_name"),
        ("Number of records", "@NoR"),
    ])

    js_resources, css_resources, script, div = get_bokeh_embed_resources(agent_bar_chart)

    return agent_bar_chart, js_resources, css_resources, script, div


def create_agent_html_graph(pipeline_name, title):
    pd.set_option("display.width", 300)
    graph_data = get_graph_statistics_for_final_stages(pipeline_name)

    panda_frame = pd.DataFrame(columns=['agent_name', 'Test', 'Startup', 'Post'])

    for index, row in enumerate(graph_data):
        f_stage = row.failure_stage
        panda_frame.loc[index] = [row.agent_name, 1 if f_stage == "TEST" else 0, 1 if f_stage == "STARTUP" else 0, 1 if f_stage == "POST" else 0]

    panda_frame = panda_frame.groupby(['agent_name']).agg(['sum', 'size']).reset_index()
    panda_frame.columns = panda_frame.columns.droplevel(1)
    panda_frame.columns = ['agent_name', 'Test', 'drop', 'Startup', 'drop', 'Post', 'NoR']
    panda_frame = panda_frame.drop('drop', 1)

    panda_frame['Test'] = round(panda_frame['Test'].astype(int)/panda_frame['NoR'] * 100, 1)
    panda_frame['Startup'] = round(panda_frame['Startup'].astype(int)/panda_frame['NoR'] * 100, 1)
    panda_frame['Post'] = round(panda_frame['Post'].astype(int)/panda_frame['NoR'] * 100, 1)
    panda_frame['Success'] = round(100 - (panda_frame['Test'] + panda_frame['Startup'] + panda_frame['Post']), 1)

    output_file(title + ".html", title=title)
    tools = "hover, previewsave"

    bar = Bar(panda_frame,
              values=blend('Success', 'Test', 'Startup', 'Post', name='tests', labels_name='test'),
              label=cat(columns='agent_name', sort=False),
              stack=cat(columns='test', sort=False),
              width=500, height=400, tools=tools, toolbar_location="above", title=title, ylabel='Agent success rate (%)')
    bar.legend.orientation = "horizontal"

    bar.set(y_range=Range1d(0, 135))

    hover = bar.select(dict(type=HoverTool))

    glyphs = bar.select(GlyphRenderer)
    for item in glyphs:
        panda_index = panda_frame['agent_name'].str.contains(item.data_source.data['agent_name'][0])
        panda_index = panda_index[panda_index == True].index[0]  # Pandas specific syntax. Ignore IDEA warning.
        item.data_source.data['NoR'] = [panda_frame.get_value(index=panda_index, col='NoR')]

    hover.tooltips = OrderedDict([
        ("Failure stage", "@test"),
        ("Rate", "@height %"),
        ("Total tests run on agent", "@NoR"),
    ])

    js_resources, css_resources, script, div = get_bokeh_embed_resources(bar)

    return bar, js_resources, css_resources, script, div


def create_job_test_html_graph(pipeline_name, title):
    graph_data = get_graph_statistics_for_final_stages(pipeline_name)
    panda_frame = pd.DataFrame(
        columns=['pipeline_counter', 'Tests passed', 'Tests failed', 'Tests skipped'])

    for index, row in enumerate(graph_data):
        panda_frame.loc[index] = [row.pipeline_counter, row.tests_run - row.tests_failed - row.tests_skipped, row.tests_failed, row.tests_skipped]

    panda_frame = panda_frame.astype(int)

    output_file(title + ".html", title=title)
    tools = "previewsave"
    # print(panda_frame)
    bar = Bar(panda_frame,
              values=blend('Tests passed', 'Tests failed', 'Tests skipped', name='tests', labels_name='test'),
              label=cat(columns='pipeline_counter', sort=False),
              stack=cat(columns='test', sort=False),
              tooltips=[('Test category', '@test'), ('Number of tests', '@height'),
                        ('Pipeline counter', '@pipeline_counter')],
              width=500, height=400, tools=tools, toolbar_location="above", title=title)
    bar.legend.orientation = "horizontal"

    height = panda_frame['Tests passed'] + panda_frame['Tests failed'] + panda_frame['Tests skipped']
    # print(height)
    height = max(height)
    # print(height)
    height_increase = 0.35 * height
    # print(height_increase)

    bar.set(y_range=Range1d(0, height + height_increase))

    js_resources, css_resources, script, div = get_bokeh_embed_resources(bar)

    return bar, js_resources, css_resources, script, div


def get_bokeh_embed_resources(chart):
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(chart, INLINE)

    return js_resources, css_resources, script, div


if __name__ == '__main__':
    create_connection()
    create_agent_html_graph('po-characterize-tests', "yolyoloylyo")
    # create_job_test_html_graph('old-system-tests', "yolyoloylyo")