import logging
from typing import Dict, List, Tuple

from core.models import (
    Coordinate,
    Method,
    Through,
    ThroughRoute,
    ThroughWalk,
    ToPlace,
    ToSomewhere,
    ToStation,
    ToStop,
)
from core.queries import (
    get_possible_routes_between_station,
    get_route_by_object_id,
    get_station_by_object_id,
)

logger = logging.getLogger(__name__)


def get_steps_between_start_station_and_final_station(
    start_station: dict, final_station: dict, start_through: Through
) -> List[List[ToStation]]:
    logger.info("Retrieve possible routes between stations")
    troncal_route_data = get_possible_routes_between_station(
        start_station["_id"], final_station["_id"]
    )

    # You must arrive to the station in some way
    base_step = ToStation(data=start_station, through=start_through)

    steps = []

    for route_data in troncal_route_data:
        through = ThroughRoute(
            method=Method.TRONCAL,
            route_data=route_data["route"],
            amount_to_arrive=route_data["destination_data"]["amount_to_arrive"],
        )
        steps.append([base_step, ToStation(data=final_station, through=through)])

    return steps


class PathBuilder:
    def __init__(
        self,
        start: Coordinate,
        final: Coordinate,
        stations_stops: Dict[str, List[dict]],
    ) -> None:
        self.start = start
        self.final = final

        self.start_stations = stations_stops["start_stations"]
        self.final_stations = stations_stops["final_stations"]
        self.start_stops = stations_stops["start_stops"]
        self.final_stops = stations_stops["final_stops"]

    def get_final_step(self, final_through: Through):
        return ToPlace(data=self.final.to_geo_json_dict(), through=final_through)

    def get_paths_between_start_stations_and_final_stations(
        self,
    ) -> List[List[ToSomewhere]]:
        return [[]]

    def get_paths_between_start_stops_and_final_stations(
        self,
    ) -> List[List[ToSomewhere]]:
        pass

    def get_paths_between_start_stations_and_final_stops(
        self,
    ) -> List[List[ToSomewhere]]:
        pass

    def get_paths_between_start_stops_and_final_stops(
        self,
    ) -> List[List[ToSomewhere]]:
        pass

    def get_all_possible_paths(self) -> List[List[ToSomewhere]]:

        paths = []

        paths.extend(self.get_paths_between_start_stations_and_final_stations())
        paths.extend(self.get_paths_between_start_stops_and_final_stations())
        paths.extend(self.get_paths_between_start_stations_and_final_stops())
        paths.extend(self.get_paths_between_start_stops_and_final_stops())

        paths = list(filter(lambda p: bool(p), paths))

        return paths


class SingleAlternativePathBuilder(PathBuilder):
    """
    Create paths base on one alternative or that allows the user to walk less
    """

    def get_start_station(self):
        return min(self.start_stations, key=lambda s: s["distance"])

    def get_final_station(self):
        return min(self.final_stations, key=lambda s: s["distance"])

    def get_troncal_steps(
        self, start_station: dict, final_station: dict, start_through: Through
    ):
        # All Stations are connected, so at least it will return a route
        all_troncal_steps = get_steps_between_start_station_and_final_station(
            start_station, final_station, start_through
        )
        return all_troncal_steps[0]

    def get_data_from_stop(self, stop: dict) -> Tuple[dict, dict]:
        # Ignore other parent stations (Special case)
        logging.info(f"Get parent station of id: {stop['parent_station']}")
        station = get_station_by_object_id(stop["parent_station"])
        logging.info(f"Get route of id: {stop['route']}")
        alimentador_route = get_route_by_object_id(stop["route"])

        return station, alimentador_route

    def get_paths_between_start_stations_and_final_stations(
        self,
    ) -> List[List[ToSomewhere]]:

        logger.info("Retrieve paths between start stations and final stations")
        if self.start_stations and self.final_stations:
            start_station = self.get_start_station()
            final_station = self.get_final_station()

            # Special case
            if start_station["_id"] == final_station["_id"]:
                return [[]]

            start_through = ThroughWalk(distance=start_station["distance"])
            troncal_steps = self.get_troncal_steps(
                start_station, final_station, start_through
            )

            final_through = ThroughWalk(distance=final_station["distance"])

            return [[*troncal_steps, self.get_final_step(final_through)]]

        return [[]]

    def get_paths_between_start_stops_and_final_stations(
        self,
    ) -> List[List[ToSomewhere]]:

        logger.info("Retrieve paths between start stops and final stations")
        if self.start_stops and self.final_stations:

            start_stop = min(self.start_stops, key=lambda s: s["distance"])
            final_station = self.get_final_station()

            start_step = ToStop(
                data=start_stop, through=ThroughWalk(distance=start_stop["distance"])
            )

            start_station, alimentador_route = self.get_data_from_stop(start_stop)

            route_through = ThroughRoute(
                method=Method.ALIMENTADOR,
                route_data=alimentador_route,
                amount_to_arrive=start_stop["amount_to_arrive"],
            )

            # Special case
            if start_station["_id"] == final_station["_id"]:
                troncal_steps = [ToStation(data=start_station, through=route_through)]
            else:
                troncal_steps = self.get_troncal_steps(
                    start_station, final_station, route_through
                )

            final_through = ThroughWalk(distance=final_station["distance"])

            return [[start_step, *troncal_steps, self.get_final_step(final_through)]]

        return [[]]

    def get_paths_between_start_stations_and_final_stops(
        self,
    ) -> List[List[ToSomewhere]]:

        logger.info("Retrieve paths between start stations and final stops")
        if self.start_stations and self.final_stops:

            start_station = self.get_start_station()
            final_stop = min(self.final_stops, key=lambda s: s["distance"])

            final_station, alimentador_route = self.get_data_from_stop(final_stop)

            start_through = ThroughWalk(distance=start_station["distance"])

            # Special case
            if start_station["_id"] == final_station["_id"]:
                troncal_steps = [ToStation(data=start_station, through=start_through)]
            else:
                troncal_steps = self.get_troncal_steps(
                    start_station, final_station, start_through
                )

            stop_step = ToStop(
                data=final_stop,
                through=ThroughRoute(
                    method=Method.ALIMENTADOR,
                    route_data=alimentador_route,
                    amount_to_arrive=final_stop["stop_sequence"],
                ),
            )

            final_through = ThroughWalk(distance=final_stop["distance"])

            return [[*troncal_steps, stop_step, self.get_final_step(final_through)]]

        return [[]]

    def get_paths_between_start_stops_and_final_stops(self) -> List[List[ToSomewhere]]:

        logger.info("Retrieve paths between start stops and final stops")
        if self.start_stops and self.final_stops:

            start_stop = min(self.start_stops, key=lambda s: s["distance"])
            final_stop = min(self.final_stops, key=lambda s: s["distance"])

            start_station, start_alimentador_route = self.get_data_from_stop(start_stop)
            final_station, final_alimentador_route = self.get_data_from_stop(final_stop)

            start_step = ToStop(
                data=start_stop, through=ThroughWalk(distance=start_stop["distance"])
            )

            route_through = ThroughRoute(
                method=Method.ALIMENTADOR,
                route_data=start_alimentador_route,
                amount_to_arrive=start_stop["amount_to_arrive"],
            )

            # Special case
            if start_station["_id"] == final_station["_id"]:
                troncal_steps = [ToStation(data=start_station, through=route_through)]
            else:
                troncal_steps = self.get_troncal_steps(
                    start_station, final_station, route_through
                )

            stop_step = ToStop(
                data=final_stop,
                through=ThroughRoute(
                    method=Method.ALIMENTADOR,
                    route_data=final_alimentador_route,
                    amount_to_arrive=final_stop["stop_sequence"],
                ),
            )

            final_through = ThroughWalk(distance=final_stop["distance"])

            return [
                [
                    start_step,
                    *troncal_steps,
                    stop_step,
                    self.get_final_step(final_through),
                ]
            ]

        return [[]]


def get_json_from_tosomewhere_steps(path: List[ToSomewhere]):
    return "[" + ",".join(map(lambda ts: ts.json(), path)) + "]"


def get_json_from_list_of_paths(paths: List[List[ToSomewhere]]):
    return "[" + ",".join(map(get_json_from_tosomewhere_steps, paths)) + "]"
