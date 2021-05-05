import os
import datetime
import click
import typing

from charts.informer import informer

def experiment(ctx: click.Context, sim_info, **kwargs):

    penetration_list: list = kwargs["penetration_list"]
    num: int = kwargs['num']
    steps: int = kwargs['steps']
    skip: int = kwargs['skip']

    simulator = ctx.obj

    del sim_info["penetration"]
    length: int = sim_info['length']
    lanes: int = sim_info['lanes']
    emergency_lane: int = sim_info["emergency_lane"]
    max_speed: int = sim_info['max_speed']
    density: float = sim_info['density']
    dispatch: int = sim_info['dispatch']
    car_length: int = sim_info['car_length']
    emergency: int = sim_info['emergency']
    pslow: float = sim_info['pslow']
    pchange: float = sim_info['pchange']
    if not sim_info["symmetry"]:
        symmetry: str = ""
    else:
        symmetry: str = "--symmetry"
    limit: int = sim_info['limit']
    
    print(sim_info["obstacles"])
    if not sim_info["obstacles"]:
        obstacles: str = ""
    else:
        lane, begin, end = sim_info['obstacles'][0]
        obstacles: str = f'--obstacles {lane}:{begin}-{end}'
    seed: typing.Optional[int] = sim_info['seed']


    if not os.path.isdir('./out'):
        os.mkdir('./out')

    date = datetime.datetime.now()
    name = str(date.date()) + '__' + str(datetime.time(date.hour, date.minute)).replace(':', '-')
    dir_name = os.path.join('out/', name)
    os.mkdir('./' + dir_name)

    informer(dir_name, steps = steps, skip = skip, penetration = penetration_list, **sim_info)

    for p in penetration_list:
        penetration = int(p * 100)
        prefix = f'p{penetration:02d}'
        for i in range(num):
            os.system(f'python src/main.py --penetration {p} --length {length} --lanes {lanes} --emergency-lane {emergency_lane} '
                      f'--max-speed {max_speed} {obstacles} --density {density} --dispatch {dispatch} '
                      f'--car-length {car_length} --emergency {emergency} --pslow {pslow} --pchange {pchange} '
                      f'{symmetry} --limit {limit} cli --steps {steps} --skip {skip} '
                      f'-o {dir_name} --prefix="{prefix}__{i:02d}" --no-charts --travel --heatmap')

        os.system(f'python src/charts/heatmap.py -o {dir_name}  -p {prefix}.traffic -s 5 {dir_name}/{prefix}__*_traffic.csv')
        os.system(f'python src/charts/travel.py -o {dir_name} -p {prefix}.travel'
                  f' {dir_name}/{prefix}__*_travel.csv')
        os.system(f'python src/charts/average.py -o {dir_name} -p {prefix}.average'
                  f' -x {penetration} {dir_name}/{prefix}__*_average.csv')

    os.system(f'python src/charts/average.py --output={dir_name} --prefix=average {dir_name}/*.average.csv')
    os.system(f'python src/charts/penetration.py --output={dir_name} --prefix=average {dir_name}/average.csv')
