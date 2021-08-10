import os
import pandas as pd
import numpy as np
import click
import typing

# @click.command()
# @click.option('--output', '-o', default=None, help='Save output to a directory')
# @click.option('--prefix', '-p', default='', help='Prefix for output file names')
# @click.argument('files', nargs=-1, type=click.File())
def travel_dataframe_generator(files): #output: typing.Optional[str], prefix: str, files):

    df = pd.DataFrame({"x": [], "travel_autonomous": [], "travel_conventional": [], "travel_emergency": [], "travel_all": []})

    for file in os.listdir(files):
        if "travel_travel" not in file and file.endswith("travel.csv") and file[0] == "p":
            current = pd.read_csv(files + "/" + file)
            current = current[current.y != 0]
            penetration = int(file[2]) if file[1] == 0 else int(file[1:3])

            df = df.append({"x": penetration, **{"travel_" + col.lower(): np.sum(current[current.type == col]["x"] * current[current.type == col]["y"] / 100) \
                                                 for col in current.type.unique().tolist()}}, ignore_index=True)

    df.sort_values(by=["x"]).set_index("x").to_csv(files + "/average_travel.csv")
    return df


#travel_dataframe_generator("/home/jezxilio/Desktop/caviar/caviar/out/2021-08-06__13-41-00/150_emergency/2_dispatch")
