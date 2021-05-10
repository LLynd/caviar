from simulator.position import Position
from simulator.road.road import Road
from simulator.vehicle.car import Car
from simulator.vehicle.vehicle import VehicleFlags
from simulator.vehicle.vehicle import Vehicle

class EmergencyCar(Car):
    emergencyRadius = 10

    def __init__(self, position: Position, velocity: int, road: Road,
                 length: int = 2, width: int = 1):
        super().__init__(position=position, velocity=velocity, road=road,
                         length=length, width=width)
        self.flags |= VehicleFlags.EMERGENCY

    def move(self) -> Position:
        x, lane = self.position
        self.velocity = min(self.velocity + 1, self._getMaxSpeed(position=self.position))
        self.position = x + self.velocity, lane
        return self.position

    def beforeMove(self) -> Position:
        self.path.append((self.position, self.velocity))
        self.last_position = self.position
        return self.position

    def giveEmergencyRadius(self) -> int:
        return cls.emergencyRadius

def isEmergency(vehicle: Vehicle) -> bool:
    return isinstance(vehicle, EmergencyCar)