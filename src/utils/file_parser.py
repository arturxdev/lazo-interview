import pandas as pd


def parse_csv(path: str) -> dict:
    df = pd.read_csv(path)
    return df.set_index(df.columns[0]).to_dict()[df.columns[1]]
