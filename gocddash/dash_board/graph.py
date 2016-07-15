from collections import OrderedDict

import pandas as pd
from bokeh.charts import Bar
from bokeh.models import HoverTool
from bokeh.plotting import *

from gocddash.analysis.data_munging import export_data_to_pandas_df


def arrange_graph_data(panda_dataframe):
    pd.options.mode.chained_assignment = None  # default='warn'
    col_list = ['result', 'agentname']
    agent_result_dataframe = panda_dataframe[col_list]
    copy_list = []
    for index, row in agent_result_dataframe.iterrows():  # Get last two digits of agent id's.
        agent = row['agentname'][-2:]
        if agent.isdigit() and int(agent) < 15:  # One of the uuid's ends in "..0058"
            copy_list.append(agent)
        else:
            copy_list.append(None)  # For pd.dropna() purposes

    copy_list = pd.DataFrame(copy_list)
    agent_result_dataframe['agentname'] = copy_list
    agent_result_dataframe['result'] = pd.to_numeric(agent_result_dataframe['result'])
    return agent_result_dataframe.dropna()


def create_agent_html_graph(pipeline_name, title):
    # TODO: Fix so that number of records is hoverable somehow. Bokeh API does not seem supportive of this atm
    # See: https://github.com/bokeh/bokeh/issues/2965

    data = export_data_to_pandas_df(pipeline_name)
    agent_result_dataframe = arrange_graph_data(data)

    nor = pd.DataFrame(columns=['agentname', 'NoR'])
    nor['NoR'] = agent_result_dataframe['agentname'].value_counts()
    nor['agentname'] = nor.index  # value_counts() does weird stuff to the agentname column. This fixes that.

    agent_result_dataframe = agent_result_dataframe.groupby(agent_result_dataframe['agentname']).mean()
    agent_result_dataframe = agent_result_dataframe.reset_index()

    agent_result_dataframe = pd.merge(agent_result_dataframe, nor, how='inner', on='agentname')

    output_file(title + ".html", title=title)
    tools = "hover,previewsave"

    plot = Bar(agent_result_dataframe, label='agentname', values='result', width=600, height=400,
               legend=None, tools=tools, title=title, agg='mean', color='#2196f3')

    hover = plot.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
        ("Success rate", "@height"),
        ("Agent Name", "@agentname"),
        # ("Number of records", "@NoR"),  # This line doesn't work for some reason
    ])

    return plot
    # Change to return the dataframe if running the mann_whitney tests in this module. Will make gocd dash stop working though.


def show_graph(plot):
    show(plot)
