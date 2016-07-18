import pandas as pd

from gocddash.util.file_storage import save_as_csv
from .data_munging import *


def build_binary_cleaned_docname_csv(pipeline_name, path):
    """ Builds a cleaned docname csv for use in ML. Currently only works on po-characterize-tests """
    # TODO: Generalise this to more pipelines than characterize

    collated_data = export_data_to_pandas_df(pipeline_name)
    failure_indices = get_failure_signatures(pipeline_name)
    id_index_pair = create_binary_test_index_list(failure_indices)
    index_dataframe = pd.DataFrame(id_index_pair)

    if pipeline_name == "po-characterize-tests":
        index_dataframe.columns = ['id', 'test_index_1', 'test_index_2', 'test_index_3', 'test_index_4', 'test_index_5',
                                   'test_index_6', 'test_index_7', 'test_index_8', 'test_index_9', 'test_index_10',
                                   'test_index_11', 'test_index_12', 'test_index_13']

        consecutive_tuple_list = pd.DataFrame(
            check_if_consecutive_failure_signature(get_failure_signatures(pipeline_name)))
        consecutive_tuple_list.columns = ['id', 'consecutive']
        index_dataframe = pd.merge(index_dataframe, consecutive_tuple_list, on='id', how='outer')

        joined_data = pd.merge(collated_data, index_dataframe, on='id', how='outer')
    else:
        joined_data = collated_data
    save_as_csv(joined_data, path)
