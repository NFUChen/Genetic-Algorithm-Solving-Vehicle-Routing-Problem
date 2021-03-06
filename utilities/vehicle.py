from typing import List, Dict
from copy import deepcopy
from random import choice


class Vehicle:
    def __init__(self,
                 capacity: int,
                 fuel_fee: int,
                 fuel_efficiency: float,
                 fixed_cost: float,
                 depots_delivery_status: List[int],
                 vehicle_name: str = None,
                 shipement_discharging_time: int = 20,
                 maximum_available_time: int = 480
                 ) -> None:
        '''
        Data Source:
        capacity:Q_k.csv
        fuel_fee: B.csv
        fuel_efficiency: a_k.csv
        fixed_cost: f_ck.csv
        depot_can_be_delivered: a_ik.csv
        '''
        self._MAXIXMUM_CAPACITY = deepcopy(capacity)
        self.capacity = capacity
        self.fuel_fee = fuel_fee
        self.fuel_efficiency = fuel_efficiency
        self.fixed_cost = fixed_cost
        self.depots_delivery_status = {depot_name: is_can_be_delivered
                                       for depot_name, is_can_be_delivered in enumerate(depots_delivery_status)}
        self._available_depots = [depot_idx
                                  for depot_idx, status in self.depots_delivery_status.items()
                                  if status == 1]
        self._all_depot_names = [name for name in self.depots_delivery_status]
        self.vehicle_name = vehicle_name
        # 固定服務時間(卸貨)為20分鐘
        self.shipement_discharging_time = shipement_discharging_time
        # 車輛使用時間限制480分鐘
        self.maximum_available_time = maximum_available_time

    @property
    def available_depots(self) -> List[int]:
        return self._available_depots

    def __repr__(self) -> str:
        capacity = f"Capacity: {self.capacity}"
        fuel_fee = f"Fuel Fee: ${self.fuel_fee}"
        fuel_efficiency = f"Fuel Efficiency: {self.fuel_efficiency} l/km"
        fixed_cost = f"Fixed Cost: ${self.fixed_cost}"
        _available_depots = f"Depots Can be Delivered: {self._available_depots}"
        sep = "-" * 60

        return "\n".join(
            [capacity,
             fuel_fee,
             fuel_efficiency,
             fixed_cost,
             _available_depots,
             sep]
        )

    def discharge(self, demand: Dict[str, int]) -> None:
        if self.is_out_of_stock():
            raise ValueError("Out of Stock")

        for product, demand_quantity in demand.items():
            if product not in self.capacity:
                raise TypeError(f"Product mismath, Vechicle doesn't have '{product}'")
            self.capacity[product] -= demand_quantity

    def replenish(self) -> None:
        self.capacity = deepcopy(self._MAXIXMUM_CAPACITY)

    def is_out_of_stock(self) -> bool:
        for product in self.capacity:
            if self.capacity[product] <= 0:
                return True
        return False

    def _is_valid_depot(self, depot_id: int) -> bool:
        return depot_id in self._all_depot_names

    def is_depot_can_be_delivered(self, depot_id: int) -> bool:
        '''
        P.S. depot_id is 1 based
        '''
        if not self._is_valid_depot(depot_id):
            raise ValueError(f"'depot_id' must be one of the following: {self._all_depot_names}")

        return depot_id in self._available_depots

    def assign_depot(self, existing_depot:List[int]) -> 'int | None':
        existing_depot_can_be_assigned = [
            depot for depot in existing_depot 
            if depot in self._available_depots
        ]
        if len(existing_depot_can_be_assigned) == 0:
            return

        return choice(existing_depot_can_be_assigned)

    def __gt__(self, _other_vehicle) -> bool:
        
        return (self.fixed_cost > _other_vehicle.fixed_cost) or (self.total_capacity > _other_vehicle.total_capacity)

    
    @property
    def total_capacity(self) -> int:
        total_capacity = 0
        for product in self.capacity:
            total_capacity = self.capacity[product]

        return total_capacity


