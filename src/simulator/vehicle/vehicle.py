import enum

from simulator.position import Position
from util.enum import withLimits


@withLimits
class VehicleFlags(enum.Flag):
    MOVED = enum.auto()
    EMERGENCY = enum.auto()


class Vehicle:
    # Vehicle properties.
    position: Position
    velocity: int
    length: int
    width: int

    # Runtime properties.
    last_position: Position
    flags: VehicleFlags

    # Statistics purposes.
    start: int

    def __init__(self, position: Position, velocity: int = 0, length: int = 2, width: int = 1):
        self.position = position
        self.velocity = velocity
        self.length = length
        self.width = width
        self.last_position = position
        self.flags = VehicleFlags.NONE

    def setStatistics(self, start: int) -> None:
        '''
        Set parameters for statistics purposes.
        :param start: starting step.
        :return: None.
        '''
        self.start = start
