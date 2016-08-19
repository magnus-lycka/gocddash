import pandas as pd


def save_as_csv(df, path):
    df.to_csv(path, index=False)


def read_data(list_of_tuples, headers):
    return pd.DataFrame(list_of_tuples, columns=headers)
