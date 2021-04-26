  
#import re
import os
import datetime
import informer

PENETRATION = [.01, .1, .2, .3, .4, .5, .6, .7, .8, .9, .99]
N = 10
STEPS = 1000
SKIP = 100

if not os.path.isdir('./out'):
    os.mkdir('./out')

date = datetime.datetime.now()
#robocza nazwa
name = str(date.date()) + '__' + str(datetime.time(date.hour, date.minute)).replace(':', '-')
dir_name = os.path.join('out/', name)
os.mkdir('./' + dir_name)

informer.informer(dir_name, penetration = PENETRATION, length = 100, lanes = 3, obstacles = "1:50-50", symmetry = True, steps = STEPS, skip = SKIP)

for p in PENETRATION: 
    penetration = int(p * 100)
    prefix = f'p{penetration:02d}'
    for i in range(N):
        os.system(f'python src/main.py --penetration {p} --length 100 --lanes 3'
                  f' --obstacles=1:50-50 --symmetry cli --steps {STEPS} --skip {SKIP}'
                  f' -o {dir_name} --prefix="{prefix}__{i:02d}" --no-charts --travel --heatmap')
        
    # files = os.listdir('./out')
    
    # files_average = []
    # files_travel = []
    # files_traffic = []
    
    # average = open(f'out/{prefix}_average.txt', 'x')
    # travel = open(f'out/{prefix}_travel.txt', 'x')
    # traffic = open(f'out/{prefix}_traffic.txt', 'x')
    
    # for file in files:
    #     search_av = re.search(f'{prefix}__(.+?)_average.csv', file)
    #     search_trav = re.search(f'{prefix}__(.+?)_travel.csv', file)
    #     search_traf = re.search(f'{prefix}__(.+?)_traffic.csv', file)
    #     if search_av: 
    #         files_average.append(search_av.group(1))
    #         average.write(f'{prefix}__{search_av.group(1)}_average.csv\n')
    #     if search_trav: 
    #         files_average.append(search_trav.group(1))
    #         average.write(f'{prefix}__{search_av.group(1)}_average.csv\n')

    #     if search_traf: 
    #         files_average.append(search_traf.group(1))
    #         average.write(f'{prefix}__{search_av.group(1)}_average.csv\n')

    # average.close()
    # travel.close()
    # traffic.close()
            
    os.system(f'python src/charts/heatmap.py -o {dir_name}  -p {prefix}.traffic -s 5 {dir_name}/{prefix}__*_traffic.csv')
    os.system(f'python src/charts/travel.py -o {dir_name} -p {prefix}.travel'
              f' {dir_name}/{prefix}__*_travel.csv')
    os.system(f'python src/charts/average.py -o {dir_name} -p {prefix}.average'
              f' -x {penetration} {dir_name}/{prefix}__*_average.csv')

os.system('python src/charts/average.py --output={dir_name} --prefix=average {dir_name}/*.average.csv')
os.system('python src/charts/penetration.py --output={dir_name} --prefix=average {dir_name}/average.csv')