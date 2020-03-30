from simulator.dispatcher.dispatcher import Dispatcher
from simulator.position import Position
from simulator.road.road import Road
from simulator.vehicle.car import Car, CarParams
from simulator.vehicle.vehicle import Vehicle


class CarDispatcher(Dispatcher):
    params: CarParams

    def __init__(self, road: Road, count: int, params: CarParams):
        super().__init__(road=road, count=count)
        self.params = params

    def _newVehicle(self, position: Position) -> Vehicle:
        speed = self.road.controller.getMaxSpeed(position)
        return Car(position, velocity=speed, road=self.road, length=self.length, params=self.params)
