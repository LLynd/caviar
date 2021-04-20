from simulator.position import Position
from simulator.road.road import Road
from simulator.vehicle.car import Car
from simulator.vehicle.obstacle import Obstacle
from simulator.vehicle.vehicle import Vehicle
from simulator.vehicle.emergency import EmergencyCar
from util.rand import shuffled


class AutonomousCar(Car):
    BlockedLane = None
    EmergencyLane = None
    def __init__(self, position: Position, velocity: int, road: Road,
                 length: int = 2, width: int = 1, limit: int = 0):
        super().__init__(
            position=position, velocity=velocity, road=road,
            length=length, width=width, limit=limit)

    def move(self) -> Position:
        x, lane = self.position
        self.velocity = min(self.velocity + 1, self._getMaxSpeed(position=self.position))
        self.position = x + self.velocity, lane
        return self.position

    @classmethod
    def updateBlockedLane(cls, value: int):
        cls.BlockedLane = value
        
    @classmethod
    def updateEmergencyLane(cls, value: int):
        cls.EmergencyLane = value

    def _tryAvoidObstacle(self) -> bool:
        x, lane = self.position
        vx, vehicle = self.road.getNextVehicle(position=self.position)
        if vehicle is None or not isinstance(vehicle, Obstacle) and lane != self.BlockedLane:
            return False
        if vx - x > max(self.velocity, 1) and lane != self.BlockedLane:
            return False
        else:
            if self.BlockedLane == None:
                self.updateBlockedLane(lane)
                print(type(self.BlockedLane))
        best_change = 0
        best_limit = self._getMaxSpeed(position=self.position)
        for change in shuffled([-self.road.lane_width, self.road.lane_width]):
            destination = (x, lane + change)
            if self._canAvoid(obstacle=vehicle, destination=destination):
                limit = self._getMaxSpeed(position=destination)
                if limit > best_limit:
                    best_change, best_limit = change, limit
        # Change to the best possible lane.
        if best_change != 0:
            destination = (x, lane + best_change)
            self._avoid(obstacle=vehicle, destination=destination)
            self.position = destination
            return True
        return False

    def _tryAvoidBlockedLane(self) -> bool:
        x, lane = self.position
        if lane == self.BlockedLane:
            for change in shuffled([-self.road.lane_width, self.road.lane_width]):
                destination = (x, lane + change)
                if self._isChangePossible(destination) == True and self._isChangeSafe(destination) == True:
                    self.position = (x, lane + change)
                    return True

    def _tryChangeEmergency(self) -> bool:
        '''
        Try changing the lane to create an emergency corridor.
        :return: if vehicle performed an emergency action.
        '''
        x, lane = self.position
        emergency = self._getEmergency()
        changeValue = self.road.lane_width // 2
        # If there is no emergency or already avoiding the emergency, continue.
        if emergency is None:
            if self.road.isSingleLane(self):
                return False
            else:
                _, absoluteLane = self.road.getAbsolutePosition(self.position)
                change = changeValue if absoluteLane == -1 else -changeValue
                # When coming back always get priority.
                return self._tryAvoidWithChange(Obstacle((-1, -1), 0, 0), change)

        # If already creating emergency corridor don't move.
        if not self.road.isSingleLane(self):
            return True
        # Decelerate slowly, cannot switch lanes when the speed is too high.
        self.velocity = max(1, self.velocity - 1)
        if self.velocity > 2:
            return True
        else:
            if self.EmergencyLane == None:
                self.updateEmergencyLane(lane)
        # Destination lane depends on the road position.
        _, absoluteLane = self.road.getAbsolutePosition(self.position)
        change = -changeValue if absoluteLane == 0 else changeValue
        self._tryAvoidWithChange(emergency, change)
        return True
    
    def _tryAvoidEmergencyLane(self) -> bool:
        x, lane = self.position
        if lane == self.EmergencyLane:
            for change in shuffled([-self.road.lane_width, self.road.lane_width]):
                destination = (x, lane + change)#max(2, self.velocity//2)
                if self._isChangePossible(destination) == True and self._isChangeSafe(destination) == True:
                    self.position = (x, lane + change)
                    return True

    def _tryChangeLanes(self) -> bool:
        # Find the best lane change.
        x, lane = self.position
        best_change = 0
        best_limit = self._getMaxSpeed(position=self.position)
        for change in shuffled([-self.road.lane_width, self.road.lane_width]):
            destination = (x, lane + change)
            if self._canChangeLane(destination):
                limit = self._getMaxSpeed(position=destination)
                if limit > best_limit:
                    best_change, best_limit = change, limit
        if best_change != 0 and lane + best_change != self.BlockedLane and lane + best_change != self.EmergencyLane:
            self.position = (x, lane + best_change)
            return True
        return False

    def _trySlowDownIfNextToEmergencyLane(self) -> bool:
        x, lane = self.position
        for l in [lane-1, lane+1]:
            if l == self.EmergencyLane and isinstance(self.road.getNextVehicle(position=(x-1,l))[1], Car):
                self.velocity = self.velocity//2  # jeszcze pomyślimy nad bardziej dynamiczną wartością
            if l == self.EmergencyLane and isinstance(self.road.getNextVehicle(position=(x-1,l))[1], EmergencyCar):
                self.velocity = self._getMaxSpeed(position=self.position)

    def _getMaxSpeedBonus(self, next: Vehicle, position: Position) -> int:
        if isinstance(next, AutonomousCar):
            return next.velocity
        return 0

    def _getSafeChangeDistance(self, previous: Vehicle, destination: Position) -> int:
        if isinstance(previous, AutonomousCar):
            return previous.velocity
        return super()._getSafeChangeDistance(previous, destination)

def isAutonomous(vehicle: Vehicle) -> bool:
    return isinstance(vehicle, AutonomousCar)
