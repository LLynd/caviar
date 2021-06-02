import os

import click
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
import typing


def make_plot(df: pd.DataFrame, key: str, ylabel: str, multiplier: int, ylim: int,
              table: bool, output, prefix) -> None:
    # Prepare data.
    key_all = f'{key}_all'
    data_all = df[['x', key_all]] \
        .rename(columns={key_all: 'y'})
    data_all['type'] = 'All'
    
    key_conventional = f'{key}_conventional'
    data_conventional = df[['x', key_conventional]] \
        .rename(columns={key_conventional: 'y'})
    data_conventional['type'] = 'Conventional'
    
    key_autonomous = f'{key}_autonomous'
    data_autonomous = df[['x', key_autonomous]] \
        .rename(columns={key_autonomous: 'y'})
    data_autonomous['type'] = 'Autonomus'
    data = data_all.append(data_conventional).append(data_autonomous)
    data['y'] *= multiplier

    if table:
        print(key)
        df[key_all] *= multiplier
        df[key_autonomous] *= multiplier
        df[key_conventional] *= multiplier
        print(df.groupby(['x'], as_index=False).agg({
            f'{key}_all': ['mean', 'std'],
            f'{key}_conventional': ['mean', 'std'],
            f'{key}_autonomous': ['mean', 'std'],
        }).to_csv(index=False, float_format='%.3f'))
    # Make plot.
    sns.set_style('white')
    f = plt.figure(figsize=(6, 4))
    f.tight_layout()
    g = sns.lineplot(x='x', y='y', hue='type', data=data)
    # Set axis title.
    if max(df[key_conventional])*multiplier >= ylim or max(df[key_autonomous])*multiplier >= ylim:
       ylim = max(max(df[key_conventional])*multiplier, max(df[key_autonomous])*multiplier) + 1
   
    g.set(xlabel='Market Penetration Rate (%)', ylabel=ylabel, ylim=(0., ylim))  # noqa: W605
    # Remove legend title.
    handles, labels = g.get_legend_handles_labels()
    g.legend(handles=handles[1:], labels=labels[1:])

    if output is not None:
        plt_path = os.path.join(output, f'{prefix}_{key}.pdf')
        plt.savefig(plt_path, bbox_inches='tight')
    else:
        plt.show()


@click.command()
@click.option('--output', '-o', default=None, help='Save output to a directory')
@click.option('--prefix', '-p', default='', help='Prefix for output file names')
@click.option('--table', '-t', is_flag=True, help='Print the output table for the graph')
@click.argument('file', type=click.File())
def main(output: typing.Optional[str], prefix: str, table: bool, file):
    df = pd.read_csv(file, header=0)
    keys = ['velocity', 'throughput', 'decelerations', 'laneChanges', 'waiting']
    ylabels = [
        'Speed (sites/step)',  # noqa: W605
        'Throughput (vehicles/step)',  # noqa: W605
        'Quick Decelerations (vehicles%/step)',  # noqa: W605
        'Lane Changes (vehicles%/step)',  # noqa: W605
        'Waiting Vehicles (vehicles%/step)'  # noqa: W605
    ]
    multipliers = [1, 1, 100, 100, 100]
    ylims = [5.5, 3.5, 6.5, 3, 60]
    for key, ylabel, multiplier, ylim in zip(keys, ylabels, multipliers, ylims):
        make_plot(df, key, ylabel, multiplier, ylim, table, output, prefix)


if __name__ == '__main__':
    main()
