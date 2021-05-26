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
    key_emergency = f'{key}_emergency'
    data_emergency = df[['x', key_emergency]] \
        .rename(columns={key_emergency: 'y'})
    data_emergency['type'] = 'Emergency'
    data = data_all.append(data_emergency)
    data['y'] *= multiplier

    if table:
        print(key)
        df[key_all] *= multiplier
        df[key_emergency] *= multiplier
        print(df.groupby(['x'], as_index=False).agg({
            f'{key}_all': ['mean', 'std'],
            f'{key}_emergency': ['mean', 'std'],
        }).to_csv(index=False, float_format='%.3f'))
    # Make plot.
    sns.set_style('white')
    f = plt.figure(figsize=(6, 4))
    f.tight_layout()
    g = sns.lineplot(x='x', y='y', hue='type', data=data)
    # Set axis title.
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
    keys = ['velocity']
    ylabels = [
        'Speed (sites/step)',  # noqa: W605
    ]
    multipliers = [1, 1, 100, 100, 100]
    ylims = [5.5, 3.5, 6.5, 3, 60]
    for key, ylabel, multiplier, ylim in zip(keys, ylabels, multipliers, ylims):
        make_plot(df, key, ylabel, multiplier, ylim, table, output, prefix)


if __name__ == '__main__':
    main()
