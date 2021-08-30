import enum
import typing

from simulator.road.road import Road
from simulator.simulator import Hook, Simulator
from simulator.statistics.averageresult import AverageResult
from simulator.vehicle.autonomous import isAutonomous
from simulator.vehicle.car import isCar
from simulator.vehicle.conventional import isConventional
from simulator.vehicle.emergency import isEmergency
from util.enum import withLimits

@withLimits
class Statistics(enum.Flag):
    VELOCITY = enum.auto()
    THROUGHPUT = enum.auto()
    HEAT_MAP = enum.auto()
    TRAVEL_TIME = enum.auto()


class Collector(Hook):
    statistics: Statistics
    skip: int
    steps: int
    emergency_lane: int
    # Velocity statistics buffers.
    velocity: typing.List[typing.List[AverageResult]]
    velocity_autonomous: typing.List[typing.List[AverageResult]]
    velocity_conventional: typing.List[typing.List[AverageResult]]
    velocity_emergency: typing.List[typing.List[AverageResult]]

    # Throughput statistics buffers.
    throughput: typing.List[typing.List[int]]

    # Heat map statistics buffers.
    heat_map: typing.List[typing.List[float]]

    # Travel time buffers.
    travel: typing.List[int]
    travel_autonomous: typing.List[int]
    travel_conventional: typing.List[int]
    travel_emergency: typing.List[int]

    def __init__(self, simulator: Simulator, statistics: Statistics = Statistics.ALL,
                 skip: int = 0, emergency_lane: int = 0):
        super().__init__(simulator=simulator)
        self.statistics = statistics
        self.skip = skip
        self.steps = 0
        self.emergency_lane = emergency_lane
        
        if self.statistics & Statistics.VELOCITY:
            self._initVelocity()
        if self.statistics & Statistics.THROUGHPUT:
            self._initThroughput()
        if self.statistics & Statistics.HEAT_MAP:
            self._initHeatMap()
        if self.statistics & Statistics.TRAVEL_TIME:
            self._initTravelTime()

    def run(self) -> None:
        self.steps += 1
        if self.steps <= self.skip:
            return

        if self.statistics & Statistics.VELOCITY:
            self._collectVelocity()
        if self.statistics & Statistics.THROUGHPUT:
            self._collectThroughput()
        if self.statistics & Statistics.HEAT_MAP:
            self._collectHeatMap()
        if self.statistics & Statistics.TRAVEL_TIME:
            self._collectTravelTime()

    @property
    def _road(self) -> Road:
        return self.simulator.road

    @property
    def _travelLimit(self) -> int:
        return int(self._road.length * 7.5)

    def _initVelocity(self):
        self.velocity = \
            [[AverageResult(0, 0) for _ in range(self._road.length)]
             for _ in range(self._road.lanes_count)]
        self.velocity_autonomous = \
            [[AverageResult(0, 0) for _ in range(self._road.length)]
             for _ in range(self._road.lanes_count)]
        self.velocity_conventional = \
            [[AverageResult(0, 0) for _ in range(self._road.length)]
             for _ in range(self._road.lanes_count)]
        self.velocity_emergency = \
            [[AverageResult(0, 0) for _ in range(self._road.length)]
             for _ in range(self._road.lanes_count)]

    def _collectVelocity(self) -> None:
        for vehicle in self._road.getAllActiveVehicles():
            last_x, _ = self._road.getAbsolutePosition(vehicle.last_position)
            cur_x, lane = self._road.getAbsolutePosition(vehicle.position)
            for x in range(last_x, cur_x):
                if x >= self._road.length:
                    continue
                value = AverageResult(value=vehicle.velocity, count=1)
                if isCar(vehicle):
                    self.velocity[lane][x] += value
                if isAutonomous(vehicle):
                    self.velocity_autonomous[lane][x] += value
                if isConventional(vehicle):
                    self.velocity_conventional[lane][x] += value
                if isEmergency(vehicle):
                    self.velocity_emergency[lane][x] += value

    def _initThroughput(self) -> None:
        self.throughput = [[0] * self._road.length for _ in range(self._road.lanes_count)]

    def _collectThroughput(self) -> None:
        for vehicle in self._road.getAllVehicles():
            last_x, _ = self._road.getAbsolutePosition(vehicle.last_position)
            cur_x, lane = self._road.getAbsolutePosition(vehicle.position)
            for x in range(last_x, cur_x):
                if x < self._road.length:
                    self.throughput[lane][x] += 1

    def getThrougput(self) -> typing.List[typing.List[float]]:
        '''
        Returns a normalized throughput, representing average throughput in a single step.
        :return: normalized throughput.
        '''
        N = float(self.steps - self.skip)
        throughput = [[.0] * self._road.length for _ in range(self._road.lanes_count)]
        for lane in range(self._road.lanes_count):
            for x in range(self._road.length):
                throughput[lane][x] = self.throughput[lane][x] / N
        return throughput

    def _initHeatMap(self) -> None:
        self.heat_map = [[.0] * self._road.length for _ in range(self._road.lanes_count)]

    def _collectHeatMap(self) -> None:
        for vehicle in self._road.getAllVehicles():
            last_x, _ = self._road.getAbsolutePosition(vehicle.last_position)
            cur_x, lane = self._road.getAbsolutePosition(vehicle.position)
            value = 1. / (cur_x - last_x + 1)
            if cur_x == last_x:
                self.heat_map[lane][cur_x] += 1.
            for x in range(last_x, cur_x):
                if x < self._road.length:
                    self.heat_map[lane][x] += value

    def getHeatMap(self) -> typing.List[typing.List[float]]:
        '''
        Returns a normalized heat map, representing average traffic in a single step.
        :return: normalized heat map.
        '''
        N = self.steps - self.skip
        heat_map = [[.0] * self._road.length for _ in range(self._road.lanes_count)]
        for lane in range(self._road.lanes_count):
            for x in range(self._road.length):
                heat_map[lane][x] = self.heat_map[lane][x] / N
        return heat_map

    def _initTravelTime(self) -> None:
        self.travel = [0] * self._travelLimit
        self.travel_autonomous = [0] * self._travelLimit
        self.travel_conventional = [0] * self._travelLimit
       
        self.travel_emergency = [0] * self._travelLimit

    def _collectTravelTime(self) -> None:
        for vehicle in self._road.removed:
            time = min(self.simulator.steps - vehicle.start, self._travelLimit - 1)
            if isCar(vehicle):
                self.travel[time] += 1
            if isAutonomous(vehicle):
                self.travel_autonomous[time] += 1
            if isConventional(vehicle):
                self.travel_conventional[time] += 1
            if isEmergency(vehicle):
                 self.travel_emergency[time] += 1
