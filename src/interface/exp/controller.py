import os
import datetime
import typing

from charts.informer import informer

def experiment(sim_info, **kwargs):

    penetration_list: list = kwargs["penetration_list"]
    dispatch_list: list = kwargs["dispatch_list"]
    emergency_list: list = kwargs["emergency_list"]
    num: int = kwargs['num']
    steps: int = kwargs['steps']
    skip: int = kwargs['skip']

    del sim_info["penetration"]
    del sim_info["dispatch"]
    del sim_info["emergency"]
    length: int = sim_info['length']
    lanes: int = sim_info['lanes']
    emergency_lane: int = sim_info["emergency_lane"]
    max_speed: int = sim_info['max_speed']
    density: float = sim_info['density']
    car_length: int = sim_info['car_length']
    pslow: float = sim_info['pslow']
    pchange: float = sim_info['pchange']
    symmetry: str = "" if not sim_info["symmetry"] else "--symmetry"
    limit: int = sim_info['limit']

    if not sim_info["obstacles"]:
        obstacles: str = ""
    else:
        sim_info["obstacles"] = [f'{lane}:{begin}-{end}' for lane, begin, end in sim_info["obstacles"]]
        obstacles: str = f'--obstacles {", ".join(sim_info["obstacles"])}'
    seed: typing.Optional[int] = sim_info['seed'] if sim_info['seed'] is not None else ""


    if not os.path.isdir('./out'):
        os.mkdir('./out')

    date = datetime.datetime.now()
    name = str(date.date()) + '__' + str(datetime.time(date.hour, date.minute)).replace(':', '-')
    dir_name = os.path.join('out/', name)
    os.mkdir('./' + dir_name)

    #ogolny informer
    informer(dir_name, steps = steps, skip = skip, num = num, penetration = penetration_list, dispatch = dispatch_list, emergency = emergency_list, **sim_info)

    #3 petle for
    for em in emergency_list:
        os.mkdir('./' + dir_name + '/' + str(em) + '_emergency')
        for d in dispatch_list:
            dir_sim = os.path.join(dir_name + '/' + str(em) + '_emergency' + '/' + str(d) + '_dispatch')
            os.mkdir('./' + dir_sim)
            informer(dir_sim, steps=steps, skip=skip, num=num, penetration=penetration_list, dispatch=d,
                     emergency=em, **sim_info)
            for p in penetration_list:
                penetration = int(p * 100)
                prefix = f'p{penetration:02d}'
                for i in range(num):
                    os.system(f'python src/main.py --penetration {p} --length {length} --lanes {lanes} --emergency-lane {emergency_lane} '
                              f'--max-speed {max_speed} {obstacles} --density {density} --dispatch {d} '
                              f'--car-length {car_length} --emergency {em} --pslow {pslow} --pchange {pchange} '
                              f'{symmetry} --limit {limit} {seed} cli --steps {steps} --skip {skip} '
                              f'-o {dir_sim} --prefix="{prefix}__{i:02d}" --no-charts --travel --heatmap')

                os.system(f'python src/charts/heatmap.py -o {dir_sim}  -p {prefix}.traffic -s 5 {dir_sim}/{prefix}__*_traffic.csv')
                os.system(f'python src/charts/travel.py -o {dir_sim} -p {prefix}.travel'
                          f' {dir_sim}/{prefix}__*_travel.csv')
                os.system(f'python src/charts/average.py -o {dir_sim} -p {prefix}.average'
                          f' -x {penetration} {dir_sim}/{prefix}__*_average.csv')

            os.system(f'python src/charts/average.py --output={dir_sim} --prefix=average {dir_sim}/*.average.csv')
            os.system(f'python src/charts/penetration.py --output={dir_sim} --prefix=average {dir_sim}/average.csv')
            if not em == 0:
                os.system(f'python src/charts/penetration_emergency.py --output={dir_sim} --prefix=average_emergency {dir_sim}/average.csv')
