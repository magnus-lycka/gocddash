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

from gocddash.analysis.domain import get_graph_statistics, get_graph_statistics_for_final_stages


def show_graph(plot):
    show(plot)


def convert_to_percentages(dataframe, column_names):
    for name in column_names:
        dataframe[name] = round(dataframe[name].astype(int) / dataframe['NoR'] * 100, 1)

    dataframe['Success'] = round(100 - (dataframe['Test'] + dataframe['Startup'] + dataframe['Post']), 1)
    return dataframe


def arrange_agent_graph_indices(dataframe):
    dataframe.columns = dataframe.columns.droplevel(1)
    dataframe.columns = ['agent_name', 'Test', 'drop', 'Startup', 'drop', 'Post', 'NoR']
    dataframe = dataframe.drop('drop', 1)
    return dataframe


def create_agent_html_graph(pipeline_name, title):
    pd.set_option("display.width", 300)
    graph_data = get_graph_statistics(pipeline_name)

    panda_frame = pd.DataFrame(columns=['agent_name', 'Test', 'Startup', 'Post'])

    for index, row in enumerate(graph_data):
        f_stage = row.failure_stage
        panda_frame.loc[index] = [row.agent_name, 1 if f_stage == "TEST" else 0, 1 if f_stage == "STARTUP" else 0,
                                  1 if f_stage == "POST" else 0]

    panda_frame = panda_frame.groupby(['agent_name']).agg(['sum', 'size']).reset_index()
    panda_frame = arrange_agent_graph_indices(panda_frame)

    panda_frame = convert_to_percentages(panda_frame, ['Test', 'Startup', 'Post'])

    # output_file(title + ".html", title=title)  # For saving as a html
    tools = "hover, previewsave"

    bar = Bar(panda_frame,
              values=blend('Success', 'Test', 'Startup', 'Post', name='tests', labels_name='test'),
              label=cat(columns='agent_name', sort=False),
              stack=cat(columns='test', sort=False),
              width=500, height=400, tools=tools, toolbar_location="right", title=title,
              ylabel='Agent success rate (%)')
    bar.legend.orientation = "horizontal"

    bar.set(y_range=Range1d(0, 135))

    hover = bar.select(dict(type=HoverTool))

    # Manually map Number of Records (NoR) to correct ColumnDataSource
    # See https://github.com/bokeh/bokeh/issues/2965 for details and possible workaround if they update the module
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
        panda_frame.loc[index] = [row.pipeline_counter, row.tests_run - row.tests_failed - row.tests_skipped,
                                  row.tests_failed, row.tests_skipped]

    panda_frame = panda_frame.groupby(['pipeline_counter']).sum().reset_index()
    panda_frame = panda_frame.astype(int)

    # output_file(title + ".html", title=title)  # For saving as a html
    tools = "previewsave"
    bar = Bar(panda_frame,
              values=blend('Tests passed', 'Tests failed', 'Tests skipped', name='tests', labels_name='test'),
              label=cat(columns='pipeline_counter', sort=False),
              stack=cat(columns='test', sort=False),
              tooltips=[('Test category', '@test'), ('Number of tests', '@height'),
                        ('Pipeline counter', '@pipeline_counter')],
              width=500, height=400, tools=tools, toolbar_location="right", title=title)
    bar.legend.orientation = "horizontal"

    height, height_increase = calculate_height_increase(panda_frame)
    bar.set(y_range=Range1d(0, height + height_increase))

    js_resources, css_resources, script, div = get_bokeh_embed_resources(bar)

    return bar, js_resources, css_resources, script, div


def calculate_height_increase(dataframe):
    height = dataframe['Tests passed'] + dataframe['Tests failed'] + dataframe['Tests skipped']
    height = max(height)
    height_increase = 0.35 * height
    return height, height_increase


def get_bokeh_embed_resources(chart):
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(chart, INLINE)

    return js_resources, css_resources, script, div
