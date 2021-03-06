from typing import Dict, List
from copy import deepcopy
from .base_class import BuilderFactory
from .route_resource_calculator import RouteResourceCalculator
from .optimizer import Optimizer


# e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
Solution = Dict[int, List[int]]


class ConstraintChecker(BuilderFactory):
    def __init__(self) -> None:
        super().__init__()
        self.resource_calc = RouteResourceCalculator()
        self.optimizer = Optimizer()

    def _is_need_to_replenish_during_delivery(self, vehicle_idx: int, route: List[int]) -> bool:
        '''
        A solution checker for checking if a given route should replenish during delivery
        '''

        copy_vehicle = deepcopy(self.vehicles[vehicle_idx])
        warehouse_depot = 0
        for depot_name in route[1:-1]:  # [0,1,2,3,0] -> [1,2,3]
            current_depot = self.depots[depot_name]
            if current_depot.depot_name == warehouse_depot:
                copy_vehicle.replenish()

            copy_vehicle.discharge(current_depot.demand)
            if copy_vehicle.is_out_of_stock():
                return True  # need to replenish

        return False

    def _is_all_depots_servered(self, solution: Solution) -> bool:
        all_depots = deepcopy(self.depots.all_depot_names)

        for route in solution.values():
            for depot_idx in route:
                if depot_idx in all_depots:
                    all_depots.remove(depot_idx)
        return len(all_depots) == 0

    def is_passing_time_window_constraints(self, vehicle_idx: int, temp_assinged_route: List[int], checking_depot_idx: int) -> bool:

        checking_depot = self.depots[checking_depot_idx]  # Depot class
        current_vehicle = self.vehicles[vehicle_idx]  # Vehicle class
        warehose_depot = 0

        # For time window constraints, we need to consider two factors.
        # (1) The delivery time starting from warehouse and going back to warehouse.
        # (2) If there exist replenishments during delivery (which we need to insert it if needed).
        checking_route = [*temp_assinged_route, checking_depot_idx]
        non_shortage_route = self.optimizer.insert_warehouse_depots_and_relenishment_points(vehicle_idx,checking_route)

        total_time_of_completing_route = self.resource_calc._calculate_time_for_current_route(vehicle_idx, non_shortage_route)


        if (total_time_of_completing_route > current_vehicle.maximum_available_time):
            return False

        # the calculating process below is for performance concern, which is helpful for avoiding duplicate computation
        # i.e., take the total time just computed above, and minus the checking depot to final destination (warehouse).
        total_time_before_arriving_checking_depot_idx = (total_time_of_completing_route - checking_depot.get_delivery_time_to_depot(warehose_depot))
        # only consider delivery time to final depot (warehose depot), so not including shipment discharging time
        total_time_before_arriving_checking_depot_idx -= current_vehicle.shipement_discharging_time

        if (total_time_before_arriving_checking_depot_idx < checking_depot.earilest_time_can_be_delivered):
            return False

        if (total_time_before_arriving_checking_depot_idx > checking_depot.latest_time_must_be_delivered):
            return False

        return True

    def is_all_depots_passing_time_window_constraints(self, vehicle_idx: int, route: List[int]) -> bool:
        # [0,1,2,3,0] -> [1,2,3]
        # is_passing_time_window_constraints will take care of inserting warehouse and inserting replenishing points.
        route_without_warehouse_depot = [depot_idx 
                                        for depot_idx in route 
                                        if depot_idx != 0]

        for checking_depot_idx in route_without_warehouse_depot:
            checking_depot_route_idx = route_without_warehouse_depot.index(checking_depot_idx)  # e.g., [1,2,3] 2 -> 1
            route_before_check_depot_idx = route_without_warehouse_depot[:checking_depot_route_idx]
            if len(route_before_check_depot_idx) < 2:  # S[], [1] -> no distance
                continue
            if checking_depot_idx not in self.depot_builder.all_depot_names_with_time_window_constraint:
                continue
            # before puting route into is_passing_time_window_constraints,
            # it needs to be processed such that [0,1,2,3,0,4,5,0] -> [1,2,3,4,5],
            # since when it is passed into the cheker function,
            # it will be processed back to what it was i.e., [0,1,2,3,0,4,5,0]
            if not self.is_passing_time_window_constraints(vehicle_idx,
                                                           route_before_check_depot_idx,
                                                           checking_depot_idx):
                return False

        return True
