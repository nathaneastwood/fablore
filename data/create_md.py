import re
import numpy as np
import pandas as pd
from py_markdown_table.markdown_table import markdown_table


def create_md_file(file: str, sort: str):
    df = pd.read_csv(file, delimiter="|").sort_values(sort).replace({np.nan: ""})
    m = markdown_table(df.to_dict(orient="records")).setParams(row_sep="markdown", quote=False).get_markdown()
    out = re.sub("csv", "md", file)
    f = open(out, "w")
    f.write("<!-- ### NOTE: This file should not be edited by hand. Please edit the .csv file. -->\n")
    f.write(m)
    f.close()


create_md_file("./src/data/animals.csv", "Name")
create_md_file("./src/data/characters.csv", "Name")
create_md_file("./src/data/food-and-drink.csv", "Name")
create_md_file("./src/data/locations.csv", "Name")
