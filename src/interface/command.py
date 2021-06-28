import random
import typing
import click
import click_config_file
import yaml

from interface.obstacle import ObstacleParamType, ObstacleValue, addObstacle
from interface.experiment_lists import PenListParamType
from interface.experiment_lists import DisListParamType
from interface.experiment_lists import EmergListParamType
from interface.gui.controller import Controller as GUIController
from interface.cli.controller import Controller as CLIController
from interface.exp.controller import experiment

from simulator.dispatcher.emergency import EmergencyDispatcher
from simulator.road.dense import DenseRoad
from simulator.road.speedcontroller import SpeedController
from simulator.simulator import Simulator
from simulator.statistics.collector import Statistics
from simulator.vehicle.conventional import Driver


def configProvider(file_path: str, cmd: str) -> typing.Dict[str, typing.Any]:
    print(f'Loading {file_path} of {cmd}')
    with open(file_path) as data:
        return yaml.safe_load(data)['simulation']


@click.group()
# Road options.
@click.option('--length', default=100, help='Road length')
@click.option('--lanes', default=8, help='Number of lanes')
@click.option('--emergency-lane', default=0, help='Lane of emergency corridor')
# Speed controller options.
@click.option('--max-speed', default=5, help='Road maximum speed')
@click.option('--obstacles', multiple=True, default=[], type=ObstacleParamType())
# Dispatcher options.
@click.option('--density', default=.1, help='Initial density of vehicles on the road')
@click.option('--dispatch', default=6, help='Maximum number of cars dispatched each step')
@click.option('--penetration', default=.5, help='Penetration rate of CAV')
@click.option('--car-length', default=2, help='Number of cells occupied by a single car')
@click.option('--emergency', default=0, help='Emergency vehicle dispatch rate')
# Driver options.
@click.option('--pslow', default=.2, help='Probability a NS-model car will slow down')
@click.option('--pchange', default=.5, help='Probability a NS-model car will change a lane')
@click.option('--symmetry', default=False, is_flag=True, help='Do not use left lane to overtake')
@click.option('--limit', default=0, help='Difference in maximum speed between vehicles')
# Other options.
@click.option('--seed', type=int, help='Seed for the RNG')
# Configuration file option.
@click_config_file.configuration_option(provider=configProvider, implicit=False)
@click.pass_context
def command(ctx: click.Context, **kwargs) -> None:
    # Extract options.
    length: int = kwargs['length']
    lanes: int = kwargs['lanes']
    emergency_lane: int = kwargs["emergency_lane"]
    max_speed: int = kwargs['max_speed']
    density: float = kwargs['density']
    dispatch: int = kwargs['dispatch']
    penetration: float = kwargs['penetration']
    car_length: int = kwargs['car_length']
    emergency: int = kwargs['emergency']
    pslow: float = kwargs['pslow']
    pchange: float = kwargs['pchange']
    symmetry: bool = kwargs['symmetry']
    limit: int = kwargs['limit']
    obstacles: typing.List[ObstacleValue] = kwargs['obstacles']
    seed: typing.Optional[int] = kwargs['seed']
    # Initialize random number generator.
    if seed is not None:
        random.seed(seed)
    # Create a road.
    speed_controller = SpeedController(max_speed=max_speed)
    road = DenseRoad(
        length=length, lanes_count=lanes, lane_width=1, emergency_lane=emergency_lane, controller=speed_controller)
    # Add obstacles.
    for obstacle in obstacles:
        addObstacle(road=road, obstacle=obstacle)
    # Create the dispatcher.
    driver = Driver(slow=pslow, change=pchange, symmetry=symmetry)
    dispatcher = EmergencyDispatcher(
        count=dispatch, road=road, penetration=penetration,
        driver=driver, length=car_length, limit=limit, emergency_rate=emergency)
    # Create the simulator and scatter vehicles.
    simulator = Simulator(road=road, dispatcher=dispatcher)
    simulator.scatterVehicles(density=density)
    ctx.obj = simulator
    global sim_info
    sim_info = kwargs

@command.command()
@click.option('--step', default=100, help='Animation time of a single simulation step (ms)')
@click.option('--fps', default=30, help='Animation frames per second')
@click.option('--buffer', default=1, help='Statistics buffer size')
@click.option('--quiet', default=0, help='Number of steps to run quietly before gui')
@click.pass_context
def gui(ctx: click.Context, step: int, fps: int, buffer: int, quiet: int) -> None:
    simulator: Simulator = ctx.obj
    for _ in range(quiet):
        simulator.step()
    controller = GUIController(simulator=simulator)
    controller.run(speed=step, refresh=fps, buffer=buffer)


@command.command()
# Simulation parameters.
@click.option('--steps', default=1000, help='Number of simulation steps to run')
@click.option('--skip', default=0, help='Skip first n steps when gathering statistics')
# Output parameters.
@click.option('--output', '-o', type=click.Path(file_okay=False), help='Output directory')
@click.option('--prefix', '-p', default='', help='Output files name prefix')
# Statistics generation.
@click.option('--no-charts', is_flag=True, help='Do not generate charts')
@click.option('--all-statistics', is_flag=True, help='Disable all statistics')
@click.option('--velocity', is_flag=True, help='Toggle velocity statistics')
@click.option('--heatmap', is_flag=True, help='Toggle heatmap statistics')
@click.option('--throughput', is_flag=True, help='Toggle throughput statistics')
@click.option('--travel', is_flag=True, help='Toggle travel time statistics')
@click.pass_context
def cli(ctx: click.Context, all_statistics: bool, velocity: bool, heatmap: bool, throughput: bool,
        travel: bool, **kwargs):
    controller = CLIController(simulator=ctx.obj)
    statistics = Statistics.ALL if all_statistics else Statistics.NONE
    if velocity:
        statistics ^= statistics.VELOCITY
    if heatmap:
        statistics ^= statistics.HEAT_MAP
    if throughput:
        statistics ^= statistics.THROUGHPUT
    if travel:
        statistics ^= statistics.TRAVEL_TIME
    controller.run(statistics=statistics, **kwargs)


@command.command()
@click.option('--penetration-list', default ='.01, .1, .2, .3, .4, .5, .6, .7, .8, .9, .99', type=PenListParamType(), help = 'Penetration rates used in an experiment')
@click.option('--num', default=10, help = 'Number of simulations in one experiment for every penetration rate')
@click.option('--steps', default=2000, help='Number of simulation steps to run')
@click.option('--skip', default=100, help='Skip first n steps when gathering statistics')
@click.option('--dispatch-list', default ='2, 4, 6', type=DisListParamType(), help = 'List of maximum numbers of cars dispatched each step in the experiment')
@click.option('--emergency-list', default ='300, 600, 900', type=EmergListParamType(), help = 'Emergency vehicle dispatch rates used in the experiment')
@click.pass_context
def exp(ctx: click.Context, **kwargs):
    experiment(sim_info, **kwargs)