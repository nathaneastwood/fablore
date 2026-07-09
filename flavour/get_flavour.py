import pandas as pd
import numpy as np


def create_flavour_md(set_id: str, card_flattened_path: str, out_file: str):
    """Create the flavour text markdown file.

    Args:
        set_id: The set ID, e.g. "OUT" for "Outsiders"
        card_flattened_path: The location of the "card-flattened.json" file in the flesh-and-blood-cards repo.
        out_file: The name of the file to create (including the .md extension).

    Returns:
        A pandas DataFrame including the set_id, id, name and flavour text. Note this function has a side effect which
        creates the markdown file.
    """
    df = pd.read_json(card_flattened_path)
    df = df[["set_id", "id", "name", "flavor_text"]]
    df = df.query("set_id in '{set_id}'".format(set_id=set_id))
    df = df.replace("", np.nan).dropna(axis=0)
    df = df.sort_values("name")
    df = df.drop_duplicates(subset=["flavor_text"])
    df = df.reset_index()

    f = open(out_file, "w")
    for index, row in df.iterrows():
        f.write("#### " + row["name"] + " - (" + row["id"] + ")\n")
        f.write(row["flavor_text"] + "\n\n")
    f.close()

    return df
