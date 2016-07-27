from collections import OrderedDict

import pandas as pd
from bokeh.charts import Bar
from bokeh.charts.attributes import cat
from bokeh.charts.operations import blend
from bokeh.embed import components
from bokeh.models import GlyphRenderer
from bokeh.models import HoverTool
from bokeh.plotting import *
from bokeh.resources import INLINE

from gocddash.analysis.domain import get_graph_statistics


def show_graph(plot):
    show(plot)


def create_agent_html_graph(pipeline_name, title):
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

    # Manually map NoR to correct ColumnDataSource
    # See https://github.com/bokeh/bokeh/issues/2965 for details and possible workaround if they update the module
    glyphs = agent_bar_chart.select(GlyphRenderer)
    for item in glyphs:
        panda_index = panda_frame['agent_name'].str.contains(item.data_source.data['agent_name'][0])
        panda_index = panda_index[panda_index == True].index[0]
        item.data_source.data['NoR'] = [panda_frame.get_value(index=panda_index, col='NoR')]

    hover.tooltips = OrderedDict([
        ("Success rate", "@height"),
        ("Agent Name", "@agent_name"),
        ("Number of records", "@NoR"),
    ])

    js_resources, css_resources, script, div = get_bokeh_embed_resources(agent_bar_chart)

    return agent_bar_chart, js_resources, css_resources, script, div


def create_job_test_html_graph(pipeline_name, title):
    graph_data = get_graph_statistics(pipeline_name)
    panda_frame = pd.DataFrame(
        columns=['pipeline_counter', 'Tests run', 'Tests failed', 'Tests skipped'])

    for index, row in enumerate(graph_data):
        panda_frame.loc[index] = [row.pipeline_counter, row.tests_run, row.tests_failed, row.tests_skipped]

    panda_frame = panda_frame.groupby(panda_frame['pipeline_counter']).agg(
        {'Tests run': 'sum', 'Tests failed': 'sum', 'Tests skipped': 'sum'}).reset_index()
    panda_frame = panda_frame.astype(int)

    output_file(title + ".html", title=title)
    tools = "previewsave"

    bar = Bar(panda_frame,
              values=blend('Tests run', 'Tests failed', 'Tests skipped', name='tests', labels_name='test'),
              label=cat(columns='pipeline_counter', sort=False),
              stack=cat(columns='test', sort=False),
              tooltips=[('Test category', '@test'), ('Number of tests', '@height'),
                        ('Pipeline counter', '@pipeline_counter')],
              width=500, height=400, tools=tools, toolbar_location="above", title=title)
    bar.legend.orientation = "horizontal"
    bar.legend.location = "top_left"

    js_resources, css_resources, script, div = get_bokeh_embed_resources(bar)

    return bar, js_resources, css_resources, script, div


def get_bokeh_embed_resources(chart):
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(chart, INLINE)

    return js_resources, css_resources, script, div


if __name__ == '__main__':
    from gocddash.analysis.data_access import create_connection

    pd.set_option('display.width', 300)
    create_connection()
    plot, js_resources, css_resources, script, div = create_agent_html_graph("protocol-rosettanet", "yololololo")
    # plot, js_resources, css_resources, script, div = create_job_test_html_graph("paysol-transformation-new", "yololololo")
    # show_graph(plot)
