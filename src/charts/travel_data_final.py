import click
import typing

from penetration_travel import make_plot
from travel_dataframe import travel_dataframe_generator

@click.command()
@click.option('--output', '-o', default=None, help='Save output to a directory')
@click.option('--prefix', '-p', default='', help='Prefix for output file names')
@click.option('--table', '-t', is_flag=True, help='Print the output table for the graph')



def main(output: typing.Optional[str], prefix: str, table: bool): #, file):
        dispatch_rates = ['2_dispatch','4_dispatch','6_dispatch']
        emergency_dispatch_rates = ['300_emergency']
        
        for emergency_dispatch in emergency_dispatch_rates:
            for dispatch_rate in dispatch_rates:
                tmp = str(output)
                travel_dataframe_generator(tmp)
                df = travel_dataframe_generator(tmp)
        
                key = 'travel'
                ylabel = 'Travel time (steps)'  # noqa: W605
                multiplier = 1
                ylim = 750
                
                make_plot(df, key, ylabel, multiplier, ylim, table, tmp, prefix, emergency=False)
                make_plot(df, key, ylabel, multiplier, ylim, table, tmp, prefix, emergency=True)


if __name__ == '__main__':
    main()

    